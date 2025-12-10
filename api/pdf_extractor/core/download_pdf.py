from concurrent.futures import ThreadPoolExecutor, as_completed
import csv
import threading
import time
from urllib.parse import quote

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from api.collector.utils.constants import API_KEY


def download_article(start: int = 0, limit: int = 0, max_threads: int = 10) -> None:
    with open("full_data.csv", "r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        data = list(reader)

        if limit == 0:
            limit = len(data) - 1

        articles_piis_list = [row["PII"]
                              for row in data if row["PII"]][start:limit]

    with ThreadPoolExecutor(max_workers=max_threads) as executor:
        futures = [
            executor.submit(get_article_pdf, data) for data in articles_piis_list
        ]
        for future in as_completed(futures):
            data = future.result()
            if data:
                print(data)


def get_article_pdf(article_pii: str):
    thread_name = threading.current_thread().name
    url: str = f"https://www.journalofdairyscience.org/action/showPdf?pii={
        quote(article_pii)
    }&api_key={API_KEY}"
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
    options.add_argument(
        "--disable-blink-features=AutomationControlled"
    )  # Ajuda a evitar detecção de bot
    prefs = {
        "download.default_directory": str(pdf_downloads),
        "plugins.always_open_pdf_externally": True,  # Baixa em vez de abrir no navegador
        "download.prompt_for_download": False,
    }

    options.add_experimental_option("prefs", prefs)

    driver = webdriver.Chrome(options=options)
    try:
        driver.get(url)

        time.sleep(10)

    except Exception as e:
        print(f"[{thread_name} Erro com PII{article_pii}: {e}")

    finally:
        driver.quit()
