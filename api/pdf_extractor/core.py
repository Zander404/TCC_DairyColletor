from builtins import print
from concurrent.futures import ThreadPoolExecutor, as_completed
import os
from pathlib import Path
import threading
import fitz
import re
from urllib.parse import quote
import time
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from api.utils.clean_text import clean_text
from api.utils.save_csv import save_csv
import csv
import asyncio

BASE_DIR = Path(__file__).resolve().parent.parent.parent
pdf_downloads = BASE_DIR / "api/downloads/"

pdf_path = BASE_DIR / "500perguntasgadoleite.pdf"
API_KEY = os.getenv("API_KEY")


async def extract_pdf():
    with open(pdf_path, "rb") as file:
        reader = fitz.open(file)
        text_total = ""

        for page in reader:
            text = page.get_text()

            text_total += text + "\n"

        text_total = re.sub(r"(\d{1,3}\n)", "", text_total)

        bloco = re.findall(
            r"(\d+\t)\s+(.*?(?:\?\s*)+)(.*?)(?=\n\d+\s+|\Z)",
            text_total,
            re.DOTALL,
        )
        result = await get_data(bloco=bloco)
        save_csv(
            "500perguntasgadoleite.csv", ["Numero", "Pergunta", "Resposta"], result
        )


def download_article(start: int = 0, limit: int = 0, max_threads: int = 10) -> None:
    with open("full_data.csv", "r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        data = list(reader)

        if limit == 0:
            limit = len(data) - 1

        articles_piis_list = [row["PII"] for row in data if row["PII"]][start:limit]

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
    url: str = f"https://www.journalofdairyscience.org/action/showPdf?pii={quote(article_pii)}&api_key={API_KEY}"
    options = Options()

    options.add_argument(
        "--headless=new"
    )  # Ou apenas "--headless" se estiver com Chrome < 112
    options.add_argument("--no-sandbox")  # CRUCIAL para Linux/Docker
    options.add_argument("--disable-gpu")  # Recomendado para headless
    options.add_argument("--window-size=1920,1080")  # Garante um tamanho de tela padrão
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


async def get_data(bloco: list) -> list:
    data = []

    for numero, pergunta, resposta in bloco:
        pergunta = clean_text(pergunta)
        resposta = clean_text(resposta)
        data.append(
            {
                "Numero": numero.replace("\t", ""),
                "Pergunta": pergunta,
                "Resposta": resposta,
            }
        )

    return data


if __name__ == "__main__":
    asyncio.run(extract_pdf())
    # get_article_pdf("S0022-0302(25)00362-5")
