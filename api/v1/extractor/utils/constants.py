import os
from pathlib import Path


CSV_FILE: str = "full_data.csv"
MAX_THREADS: int = 10
PDF_DOWNLOAD_WAIT = 10


EXTRACTOR_PATH = Path(__file__).parent.parent
USER_DATA_DIR = "./browser_session"
API_KEY = os.getenv("API_KEY")
