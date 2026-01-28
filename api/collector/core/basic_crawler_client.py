from abc import ABC, abstractmethod
from typing import List
from curl_cffi import AsyncSession
from parsel import Selector
from api.logger import logger
from pathlib import Path
import httpx
import asyncio
import random
import unicodedata


class BaseCrawler(ABC):
    def __init__(self, base_url: str, output_dir="downloads") -> None:
        self.base_url = base_url
        self.output_path = Path(output_dir)

        self.output_path.mkdir(parents=True, exist_ok=True)
        self.client = httpx.Client(follow_redirects=True)

    @abstractmethod
    def get_pdf_link(self, html_content: str) -> str:
        "Extair o link de downloads dos PDF's da pagina HTML"
        pass

    @abstractmethod
    def handlePagination(self, html_content: str) -> str:
        "Procurar o URL para a a próxima página"
        pass

    def download_file(self, url: str):
        try:
            response = self.client.get(url=url)
            filename = url.split("/")[-1] or "file.pdf"
            path = self.output_path / filename

            with open(path, "wb") as f:
                f.write(response.content)
            logger.info(f"Download Concluido: {url}")

        except httpx.HTTPStatusError as e:
            logger.error(f" Erro HTTP ao baixar o pdf {url}: {e}")
