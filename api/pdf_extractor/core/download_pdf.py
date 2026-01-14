from concurrent.futures import ThreadPoolExecutor, as_completed
import csv
import threading
import time
from typing import List
from urllib.parse import quote

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from api.collector.utils.constants import API_KEY


CSV_FILE: str = "full_data.csv"
MAX_THREADS: int = 10
PDF_DOWNLOAD_WAIT = 10


def download_article(
    start: int = 0, limit: int = 0, max_threads: int = MAX_THREADS
) -> None:
    with open(CSV_FILE, "r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        rows = list(reader)

        if limit == 0:
            limit = len(rows) - 1

    article_piis: List[str] = [
        row["PII"] for row in rows[start:limit] if row.get("PII")
    ]

    with ThreadPoolExecutor(max_workers=max_threads) as executor:
        tasks = [executor.submit(get_article_pdf, pii) for pii in article_piis]
        for task in as_completed(tasks):
            task.result()


def get_article_pdf(article_pii: str):
    thread_name: str = threading.current_thread().name
    url: str = f"https://www.journalofdairyscience.org/action/showPdf?pii={
        quote(article_pii)
    }&api_key={API_KEY}"

    driver = _create_chrome_drive_config()

    try:
        driver.get(url)

        time.sleep(PDF_DOWNLOAD_WAIT)

    except Exception as e:
        print(f"[{thread_name} Erro com PII{article_pii}: {e}")

    finally:
        driver.quit()


def _create_chrome_drive_config() -> webdriver.Chrome:
    options = Options()
    options.add_argument(
        "--headless=new"
    )  # Ou apenas "--headless" se estiver com Chrome < 112
    options.add_argument("--no-sandbox")  # CRUCIAL para Linux/Docker
    options.add_argument("--disable-gpu")  # Recomendado para headless
    # Garante um tamanho de tela padrão
    options.add_argument("--window-size=1920,1080")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
    options.add_argument("--disable-blink-features=AutomationControlled")

    prefs = {
        "download.default_directory": str(pdf_downloads),
        "plugins.always_open_pdf_externally": True,  # Baixa em vez de abrir no navegador
        "download.prompt_for_download": False,
    }

    options.add_experimental_option("prefs", prefs)

    return webdriver.Chrome(options=options)
