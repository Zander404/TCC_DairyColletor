import logging

logger_name: str = "Crawler_LOG"
logs_filename: str = "crawler_logs"


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler(logs_filename), logging.StreamHandler()],
)
logger = logging.getLogger(logger_name)
