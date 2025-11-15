import logging
from pathlib import Path


class Logger:
    """Encapsulates logging configuration and provides a logger instance."""

    def __init__(self, name="chat_app", log_file=None):
        LOG_DIR = Path(__file__).parent.parent / "logs"
        LOG_DIR.mkdir(exist_ok=True)
        self.log_file = log_file or (LOG_DIR / "app.log")

        logging.basicConfig(
            level=logging.INFO,
            format="[%(asctime)s] %(levelname)s in %(module)s: %(message)s",
            handlers=[logging.FileHandler(self.log_file), logging.StreamHandler()],
        )
        self.logger = logging.getLogger(name)

    def get_logger(self):
        return self.logger
