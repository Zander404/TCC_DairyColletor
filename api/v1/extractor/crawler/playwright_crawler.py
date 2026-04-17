import asyncio
import os
from pathlib import Path
import shutil
from typing import List
from urllib.parse import quote
from playwright.async_api import async_playwright
from api.v1.extractor.utils.constants import (
    API_KEY,
    URL_JDS_BASE,
    URL_JDS_DONWLOAD_PDF,
    USER_DATA_DIR,
)
from api.v1.extractor.utils.constants import EXTRACTOR_PATH


class PlayWrightCrawler:
    def __init__(self, downloads_dir: str = "downloads"):
        self.download_dir = EXTRACTOR_PATH / "data" / downloads_dir
        self.download_dir.mkdir(parents=True, exist_ok=True)

        self.semaphore = asyncio.Semaphore(3)

    async def download_all(self, piis_list: List[str]):
        cookie_auth_dir = await self.create_master_auth()

        tasks = [self._download_article(pii, cookie_auth_dir) for pii in piis_list]
        await asyncio.gather(*tasks)

    async def _download_article(self, article_pii: str, cookie_auth_dir) -> None:
        url = f"{URL_JDS_DONWLOAD_PDF}?pii={quote(article_pii)}&api_key={API_KEY}"
        session_path = Path(USER_DATA_DIR) / f"session_{article_pii}"

        async with self.semaphore:
            if os.path.exists(session_path):
                shutil.rmtree(session_path, ignore_errors=True)
            shutil.copytree(cookie_auth_dir, session_path, dirs_exist_ok=True)

            async with async_playwright() as p:
                context = await p.chromium.launch_persistent_context(
                    user_data_dir=session_path,
                    headless=False,
                    accept_downloads=True,
                    args=[
                        "--no-sandbox",
                        "--disable-blink-features=AutomationControlled",
                    ],
                )

                page = context.pages[0]

                try:
                    # 1. Interceptamos a requisição do PDF
                    # Em vez de deixar o browser baixar, nós mesmos pegamos os bytes
                    async with page.expect_response(
                        lambda res: "showPdf" in res.url and res.status == 200,
                        timeout=90000,
                    ) as response_info:
                        await page.goto(url, wait_until="commit")

                    response = await response_info.value

                    # 2. Verificamos se o conteúdo é realmente um PDF
                    content_type = response.headers.get("content-type", "")
                    if "application/pdf" in content_type:
                        # Lemos o corpo da resposta (os bytes do PDF)
                        pdf_body = await response.body()

                        save_path = self.download_dir / f"{article_pii}.pdf"
                        with open(save_path, "wb") as f:
                            f.write(pdf_body)

                        print(f"✓ Sucesso: {article_pii} (Download via Stream)")
                    else:
                        print(
                            f"✘ Falha: Resposta não é PDF (Status: {response.status})"
                        )

                except Exception as e:
                    print(f"✘ Erro no PII {article_pii}: {str(e)}")
                finally:
                    await context.close()

                    await asyncio.sleep(1)
                    shutil.rmtree(session_path, ignore_errors=True)

    async def create_master_auth(self):
        master_path = Path(USER_DATA_DIR) / "master_session"
        master_path.mkdir(parents=True, exist_ok=True)

        async with async_playwright() as p:
            context = await p.chromium.launch_persistent_context(
                user_data_dir=str(master_path),
                headless=False,
                args=[
                    "--no-sandbox",
                    "--disable-extensions",
                    "--disable-blink-features=AutomationControlled",
                ],
            )
            page = context.pages[0]
            await page.goto(URL_JDS_BASE)

            while context.pages:
                await asyncio.sleep(1)
                try:
                    if not context.pages:
                        break
                except:
                    break

            await context.close()
        return master_path
