from abc import ABC, abstractmethod
from pathlib import Path
import re
from typing import List

from parsel import Selector
from api.logger import logger
from curl_cffi import AsyncSession

import asyncio
import random
import unicodedata


class BaseAsyncCrawler(ABC):
    def __init__(self, base_url, output_dir="downloads", max_concurrent=1):
        self.base_url = base_url
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.queue = asyncio.Queue()
        self.max_concurrent = max_concurrent  # Limite de downloads simultâneos

        # Headers que imitam um navegador Chrome atualizado
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Cache-Control": "max-age=0",
        }

    async def _random_wait(self):
        await asyncio.sleep(random.uniform(2.0, 5.0))

    @abstractmethod
    def get_pdf_links(self, html_content: str) -> List[str]:
        "Extair o link de downloads dos PDF's da pagina HTML"
        pass

    @abstractmethod
    def get_next_page(self, html_content: str) -> str | None:
        "Procurar o URL para a a próxima página"
        pass

    def file_exists(self, filename: str) -> bool:
        """Verifica se o arquivo já existe na pasta de destino."""
        path = self.output_dir / filename
        if path.exists():
            logger.info(f"⏩ Pulando (já existe): {filename}")
            return True
        return False

    def _sanitaze_filename(self, filename: str) -> str:
        filename = (
            unicodedata.normalize("NFKD", filename)
            .encode("ascii", "ignore")
            .decode("ascii")
        )

        filename = re.sub(r"[^\w\s-]", "", filename).strip()
        return re.sub(r"[-\s]+", "_", filename)

    async def download_worker(self):
        async with AsyncSession(impersonate="chrome120") as s:
            while True:
                pdf_url, suggested_name = await self.queue.get()

                try:
                    await self._random_wait()
                    clean_name: str = self._sanitaze_filename(suggested_name)
                    path: Path = self.output_dir / f"{clean_name}.pdf"

                    resp = await s.get(pdf_url, timeout=30.0)

                    # 1. Verificação de Duplicado (Economiza requisições)
                    if self.file_exists(str(path)):
                        continue

                    # Se o conteúdo não for PDF, é uma página de visualização
                    if "text/html" in resp.headers.get("Content-Type", ""):
                        logger.info(
                            f"Link de visualizador detectado em {pdf_url}. Extraindo link real..."
                        )
                        sel = Selector(text=resp.text)
                        real_pdf_url = (
                            sel.css("a[href$='.pdf']::attr(href)").get()
                            or sel.css("meta[property='og:url']::attr(content)").get()
                        )

                        if real_pdf_url:
                            resp = await s.get(real_pdf_url, timeout=30.0)

                    # Salva o arquivo apenas se for PDF de fato
                    if (
                        resp.status_code == 200
                        and "application/pdf" in resp.headers.get("Content-Type", "")
                    ):
                        with open(path, "wb") as f:
                            f.write(resp.content)
                        logger.info(f"Arquivo salvo: {path.name}")

                except Exception as e:
                    logger.error(f"Falha ao processar {pdf_url}: {e}")
                finally:
                    self.queue.task_done()

    async def producer(self, start_url):
        """Produtor: Navega pelas páginas e alimenta a fila."""
        current_url = start_url
        async with AsyncSession(impersonate="chrome120") as s:
            while current_url:
                try:
                    await self._random_wait()
                    logger.info(f"Explorando: {current_url}")
                    resp = await s.get(current_url, timeout=30.0)
                    resp.raise_for_status()

                    links = self.get_pdf_links(resp.text)
                    for pdf_url, title in links:
                        # Normalização de URL relativa
                        full_link = (
                            pdf_url
                            if pdf_url.startswith("http")
                            else f"{self.base_url.rstrip('/')}/{pdf_url.lstrip('/')}"
                        )
                        await self.queue.put((full_link, title))

                    current_url = self.get_next_page(resp.text)

                except Exception as e:
                    logger.error(f" Erro na navegação: {current_url} | Erro: {e}")
                    break

    async def run(self, start_url: str):
        workers = [
            asyncio.create_task(self.download_worker())
            for _ in range(self.max_concurrent)
        ]
        await self.producer(start_url)
        await self.queue.join()

        for w in workers:
            w.cancel()
            logger.info("--Processamento Finalizado---")
