import logging
from app.core.config import settings


def setup_logging():
    logging.basicConfig(level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO))
    return logging.getLogger(__name__)


logger = setup_logging()
