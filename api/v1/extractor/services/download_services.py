import asyncio
from concurrent.futures import ThreadPoolExecutor, as_completed
import csv
import io
import os
import threading
import time
from urllib.parse import quote
from fastapi import UploadFile
from selenium import webdriver
import undetected_chromedriver as uc


from playwright.async_api import Playwright, async_playwright
from playwright_stealth import Stealth

from selenium.webdriver.chrome.options import Options
from api.v1.collector.utils.constants import API_KEY
from api.v1.extractor.utils.constants import (
    EXTRACTOR_PATH,
    MAX_THREADS,
    PDF_DOWNLOAD_WAIT,
    USER_DATA_DIR,
)


class DownloadServices:
    def __init__(self, input_pdf_path: str = "input"):
        self.pdfs_path = EXTRACTOR_PATH / "data" / input_pdf_path
        self.semaphore = asyncio.Semaphore(3)

        self.pdfs_path.mkdir(parents=True, exist_ok=True)

    async def download_article(
        self,
        input_file: UploadFile,
        start: int = 0,
        limit: int = 0,
        max_threads: int = MAX_THREADS,
    ) -> None:

        content = await input_file.read()
        decoded_content = content.decode("utf-8")

        temp_input_file: io.StringIO = io.StringIO(decoded_content)

        reader = csv.DictReader(temp_input_file)
        rows = list(reader)

        if limit == 0:
            limit = len(rows)

        article_piis: list[str] = [
            row["PII"] for row in rows[start:limit] if row.get("PII")
        ]

        with ThreadPoolExecutor(max_workers=max_threads) as executor:
            tasks = [executor.submit(self.get_article_pdf, pii) for pii in article_piis]
            for task in as_completed(tasks):
                task.result()

        temp_input_file.close()
        await input_file.close()

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

            time.sleep(100)

        except Exception as e:
            print(f"[{thread_name} Erro com PII{article_pii}: {e}")

        finally:
            driver.quit()

    async def download_all(self, input_file: UploadFile, start: int, limit: int):

        content = await input_file.read()
        decoded_content = content.decode("utf-8")

        temp_input_file: io.StringIO = io.StringIO(decoded_content)

        reader = csv.DictReader(temp_input_file)
        rows = list(reader)

        if limit == 0:
            limit = len(rows)

        pii_list: list[str] = [
            row["PII"] for row in rows[start:limit] if row.get("PII")
        ]

        tasks = [self.get_article_pdf_playwright(pii) for pii in pii_list]
        await asyncio.gather(*tasks)

    async def get_article_pdf_playwright(self, article_pii: str):
        url: str = f"https://www.journalofdairyscience.org/action/showPdf?pii={quote(article_pii)}&api_key={API_KEY}"

        # O Semáforo garante que só entram 'X' tarefas por vez aqui
        async with self.semaphore:
            # Nova sintaxe do Stealth
            async with Stealth().use_async(async_playwright()) as p:
                browser = await p.chromium.launch_persistent_context(
                    user_data_dir=USER_DATA_DIR,
                    headless=False,
                    args=[
                        "--disable-blink-features=AutomationControlled",
                        "--no-sandbox",
                    ],
                    extra_http_headers={
                        "Accept": "application/pdf"  # Diz que você quer o arquivo puramente
                    },
                )
                await browser.add_init_script("""
                    Object.defineProperty(navigator, 'plugins', {
                        get: () => { return { length: 0 }; }
                    });
                """)

                page = browser.pages[0]

                try:
                    async with page.expect_download(timeout=90000) as download_info:
                        # Aumentar o timeout para 60s (Cloudflare pode demorar)
                        await page.goto(url, wait_until="commit")
                        download = await download_info.value
                        await download.save_as(self.pdfs_path / f"{article_pii}.pdf")

                except Exception as e:
                    print(f"[{article_pii}] Erro: {e}")
                finally:
                    await browser.close()

    def _create_chrome_drive_config(self) -> webdriver.Chrome:
        options = uc.ChromeOptions()

        # FIX:  AGR o  Journal of Dairy Science está com  CAPTCHA
        # options.add_argument(
        #     "--headless=new"
        # )  # Ou apenas "--headless" se estiver com Chrome < 112
        # options.add_argument("--no-sandbox")  # CRUCIAL para Linux/Docker
        # options.add_argument("--disable-gpu")  # Recomendado para headless
        # # Garante um tamanho de tela padrão
        # options.add_argument("--window-size=1920,1080")
        #
        # options.add_argument(
        #     "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        # )
        # options.add_argument("--disable-infobars")
        #
        # ### Remover Flag de Automacao
        # options.add_argument("--disable-blink-features=AutomationControlled")
        # options.add_experimental_option("excludeSwitches", ["enable-automation"])
        # options.add_experimental_option("useAutomationExtension", False)
        #
        # prefs = {
        #     "download.default_directory": str(self.pdfs_path),
        #     "plugins.always_open_pdf_externally": True,  # Baixa em vez de abrir no navegador
        #     "download.prompt_for_download": False,
        # }
        #
        # options.add_experimental_option("prefs", prefs)
        #
        # return webdriver.Chrome(options=options)
        #
        options.binary_location = f"{os.getcwd()}/usr/bin/chromium"
        prefs = {
            "download.default_directory": str(self.pdfs_path),
            "plugins.always_open_pdf_externally": True,
            "download.prompt_for_download": False,
        }
        options.add_experimental_option("prefs", prefs)

        profile_dir = os.path.join(os.getcwd(), "perfil_automacao")

        options.add_argument(f"--user-data-dir={os.path.join(profile_dir)}")

        # Use o UC para criar o driver, não o webdriver comum
        return uc.Chrome(options=options, headless=False)
