import logging
import sys

# Standard log format
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - [%(request_id)s] - %(message)s"

class RequestIdFilter(logging.Filter):
    """
    Filter that ensures request_id is always present in the log record.
    """
    def filter(self, record):
        if not hasattr(record, "request_id"):
            record.request_id = "N/A"
        return True

def setup_logging():
    # Root logger configuration
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    # Console handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.INFO)

    formatter = logging.Formatter(LOG_FORMAT)
    handler.setFormatter(formatter)
    handler.addFilter(RequestIdFilter())

    # Avoid duplicate handlers if setup is called multiple times
    if root_logger.hasHandlers():
        root_logger.handlers.clear()

    root_logger.addHandler(handler)

    # Silence noise from third party libraries
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING) # Set to INFO if needed for SQL logs

setup_logging()
logger = logging.getLogger("app")
