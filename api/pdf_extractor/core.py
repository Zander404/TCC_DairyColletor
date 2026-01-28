import os
from pathlib import Path
from api.pdf_extractor.core.extract_pdf import extract_pdf
import asyncio

BASE_DIR = Path(__file__).resolve().parent.parent.parent
pdf_downloads = BASE_DIR / "api/downloads/"

pdf_path = BASE_DIR / "500perguntasgadoleite.pdf"
API_KEY = os.getenv("API_KEY")


if __name__ == "__main__":
    asyncio.run(extract_pdf())
