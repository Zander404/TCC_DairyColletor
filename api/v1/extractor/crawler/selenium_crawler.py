import asyncio
from concurrent.futures import ThreadPoolExecutor
import os
import threading
import time
from typing import List
from urllib.parse import quote
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from api.v1.extractor.utils.constants import API_KEY, MAX_THREADS
from api.v1.extractor.utils.constants import EXTRACTOR_PATH, PDF_DOWNLOAD_WAIT


class SeleniumCrawler:
    def __init__(self, download_dir: str = "downloads") -> None:
        self.pdfs_path = EXTRACTOR_PATH / download_dir

    async def download_all(
        self,
        piis_list: List[str],
        max_threads: int = MAX_THREADS,
    ) -> None:

        loop = asyncio.get_event_loop()

        with ThreadPoolExecutor(max_workers=max_threads) as executor:
            tasks = [
                loop.run_in_executor(executor, self.get_article_pdf, pii)
                for pii in piis_list
            ]
            await asyncio.gather(*tasks)

    def get_article_pdf(self, article_pii: str):
        thread_name: str = threading.current_thread().name
        url: str = f"https://www.journalofdairyscience.org/action/showPdf?pii={quote(article_pii)}&api_key={API_KEY}"

        driver = self._create_chrome_drive_config()
        driver.execute_script(
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
        )

        try:
            driver.get(url)

            ## ESPERAR QUE O PDF SEJA BAIXADO:
            for _ in range(PDF_DOWNLOAD_WAIT):
                if any(f.endswith(".pdf") for f in os.listdir(self.pdfs_path)):
                    break

            time.sleep(3.5)

        except Exception as e:
            print(f"[{thread_name} Erro com PII{article_pii}: {e}")

        finally:
            driver.quit()

    def _create_chrome_drive_config(self) -> webdriver.Chrome:
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
        options.add_argument("--disable-infobars")

        ### Remover Flag de Automacao
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)

        prefs = {
            "download.default_directory": str(self.pdfs_path),
            "plugins.always_open_pdf_externally": True,  # Baixa em vez de abrir no navegador
            "download.prompt_for_download": False,
        }

        options.add_experimental_option("prefs", prefs)

        return webdriver.Chrome(options=options)
