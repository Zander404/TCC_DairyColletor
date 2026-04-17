import os
from pathlib import Path

# URL
"""
URL para as etapas de Download
"""

URL_JDS_BASE: str = "https://www.journalofdairyscience.org"
URL_JDS_DONWLOAD_PDF: str = "https://www.journalofdairyscience.org/action/showPdf"  # Journal of Dairy Science para Download de PDF


CSV_FILE: str = "full_data.csv"
MAX_THREADS: int = 10
PDF_DOWNLOAD_WAIT: int = 10


EXTRACTOR_PATH: Path = Path(__file__).parent.parent
USER_DATA_DIR: str = "./browser_session"
API_KEY = os.getenv("API_KEY")
