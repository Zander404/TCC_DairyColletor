import os

import logging
from datetime import datetime

os.makedirs("logs", exist_ok=True)
logger_name: str = "CRAWLER_PDF"
logger_filename: str = f"logs/crawler_{datetime.now().strftime('%Y-%m-%d')}.log"


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(logger_filename, encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(logger_name)
