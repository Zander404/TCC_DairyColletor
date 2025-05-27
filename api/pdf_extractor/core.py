from builtins import print
from os import wait
import os
from pathlib import Path
import fitz
import re
from urllib.parse import quote
import time
import asyncio
from playwright.sync_api import sync_playwright
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from api.utils.clean_text import clean_text
from api.utils.save_csv import save_csv
import requests

BASE_DIR = Path(__file__).resolve().parent.parent.parent

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


def get_article_pdf(article_pii: str):
    url: str = f"https://www.journalofdairyscience.org/action/showPdf?pii={quote(article_pii)}&api_key={API_KEY}"
    options = Options()
    # options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")

    prefs = {
        "download.default_directory": "/home/xandy/TCC/tcc_collector/",
        "plugins.always_open_pdf_externally": True,  # Baixa em vez de abrir no navegador
        "download.prompt_for_download": False,
    }

    options.add_experimental_option("prefs", prefs)

    driver = webdriver.Chrome(options=options)

    driver.get(url)
    time.sleep(5)

    cookies = driver.get_cookies()

    driver.quit()

    cookies_dict = {cookie["name"]: cookie["value"] for cookie in cookies}

    response = requests.get(url, cookies=cookies_dict)
    print(response.content)
    with open("artigo.pdf", "wb") as f:
        f.write(response.content)


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
    # asyncio.run(extract_pdf())
    get_article_pdf("S0022-0302(25)00362-5")
