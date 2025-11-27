.PHONY: format clean lint

format:
	autoflake --remove-all-unused-imports --remove-unused-variables --in-place --recursive .
	isort .
	black .

lint:
	ruff check .
	black --check .

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete