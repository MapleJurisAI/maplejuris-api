"""Retrieval agent module for semantic search over legal sections.

This module defines a retrieval agent that uses LangChain, pgvector, and OpenAI
to perform similarity search over embedded legal sections and return relevant results.
"""

from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from sqlalchemy import create_engine, text

from utils.logger import Logger

logger = Logger().get_logger()
load_dotenv()


class RetrievalAgent:
    """Retrieval agent for semantic search over legal sections.

    Attributes:
        embeddings: OpenAI embeddings model for encoding queries.
        engine: SQLAlchemy engine for database connections.
    """

    def __init__(
        self,
        connection_string: str,
        model_name: str = "text-embedding-3-small",
    ):
        """Initialize the retrieval agent with database connection.

        Args:
            connection_string: PostgreSQL database connection string.
            model_name: Name of the OpenAI embedding model. Defaults to "text-embedding-3-small".

        Raises:
            ValueError: If connection string is invalid.
            Exception: For other unexpected initialization errors.
        """
        try:
            logger.info("Initializing retrieval agent")

            # Initialize embeddings for encoding queries
            logger.info(f"Initializing embeddings with model: {model_name}")
            self.embeddings = OpenAIEmbeddings(model=model_name)

            # Create database engine
            logger.info("Creating database engine")
            self.engine = create_engine(connection_string)

            logger.info("Retrieval agent initialized successfully")

        except ValueError as e:
            logger.error(f"Invalid configuration: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during initialization: {e}")
            raise

    def process(self, query: str, k: int = 5) -> list[dict]:
        """Perform similarity search and return relevant sections.

        Args:
            query: The search query string.
            k: Number of results to return. Defaults to 5.

        Returns:
            List of dictionaries containing section information:
            - text: The section text
            - metadata: Section metadata (label, statute info, etc.)
            - score: Similarity score (distance)

        Raises:
            ValueError: If the query is empty or invalid.
            Exception: For errors during retrieval.
        """
        try:
            if not query or not query.strip():
                raise ValueError("Query cannot be empty")

            logger.info(f"Searching for: {query[:50]}... (k={k})")

            # Encode query to embedding
            query_embedding = self.embeddings.embed_query(query)

            # Convert embedding list to PostgreSQL vector format string
            embedding_str = "[" + ",".join(map(str, query_embedding)) + "]"

            # Perform similarity search using pgvector
            # Using cosine distance (1 - cosine similarity)
            # Note: We embed the vector string directly in the query since SQLAlchemy text()
            # doesn't handle ::vector casts well with parameter binding
            # The embedding_str is safe here as it's generated from our embedding model, not user input
            similarity_query = text(
                f"""
                SELECT 
                    s.id,
                    s.label,
                    s.text,
                    s.position,
                    st.short_title as statute_title,
                    st.long_title as statute_long_title,
                    1 - (s.embedding <=> '{embedding_str}'::vector) as similarity
                FROM sections s
                JOIN bodies b ON s.body_id = b.id
                JOIN statutes st ON b.statute_id = st.id
                WHERE s.embedding IS NOT NULL
                  AND s.text IS NOT NULL
                  AND s.text != ''
                ORDER BY s.embedding <=> '{embedding_str}'::vector
                LIMIT :k
            """
            )

            with self.engine.connect() as conn:
                result = conn.execute(
                    similarity_query,
                    {"k": k},
                )
                rows = result.fetchall()

            # Format results
            formatted_results = []
            for row in rows:
                formatted_results.append(
                    {
                        "id": str(row.id),
                        "text": row.text,
                        "label": row.label,
                        "position": row.position,
                        "statute_title": row.statute_title,
                        "statute_long_title": row.statute_long_title,
                        "similarity": float(row.similarity),
                    }
                )

            logger.info(f"Retrieved {len(formatted_results)} results")
            return formatted_results

        except ValueError as e:
            logger.error(f"Invalid query: {e}")
            raise
        except Exception as e:
            logger.error(f"Error during retrieval: {e}")
            raise


if __name__ == "__main__":
    try:
        import os

        from dotenv import load_dotenv

        load_dotenv()

        # Get connection details from environment or use defaults
        # For peer authentication (no user/password), use: postgresql:///maplejuris
        # Or specify: postgresql://username@localhost:5432/maplejuris
        db_host = os.getenv("SQL_HOST", "localhost")
        db_port = os.getenv("SQL_PORT", "5432")
        db_name = os.getenv("SQL_DATABASE", "maplejuris")
        db_user = os.getenv("SQL_USER", "")
        db_password = os.getenv("SQL_PASSWORD", "")

        # Build connection string
        if not db_user:
            # Peer authentication
            connection_string = f"postgresql:///{db_name}"
        elif db_password:
            connection_string = (
                f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
            )
        else:
            connection_string = f"postgresql://{db_user}@{db_host}:{db_port}/{db_name}"

        retrieval_agent = RetrievalAgent(connection_string=connection_string)
        query = "What are the penalties for theft?"
        results = retrieval_agent.process(query, k=5)
        for i, result in enumerate(results, 1):
            print(f"\nResult {i} (similarity: {result['similarity']:.4f}):")
            print(f"Statute: {result['statute_title']}")
            print(f"Section: {result['label']}")
            print(f"Text: {result['text'][:200]}...")
    except Exception as e:
        logger.error(f"Failed to run retrieval agent: {e}")
