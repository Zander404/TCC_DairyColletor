import asyncio
import csv
import io
from typing import Literal
from fastapi import UploadFile
from api.v1.extractor.crawler.playwright_crawler import PlayWrightCrawler
from api.v1.extractor.crawler.selenium_crawler import SeleniumCrawler
from api.v1.extractor.utils.constants import EXTRACTOR_PATH


class DownloadServices:
    def __init__(self, input_pdf_path: str = "input"):
        self.pdfs_path = EXTRACTOR_PATH / "data" / input_pdf_path
        self.semaphore = asyncio.Semaphore(3)

        self.pdfs_path.mkdir(parents=True, exist_ok=True)

    async def download_all(
        self,
        input_file: UploadFile,
        start: int,
        limit: int,
        crawler_option: Literal["PLAYWRIGHT", "SELENIUM"] = "PLAYWRIGHT",
    ):

        # Convert the input_file
        #
        input_content = await input_file.read()
        decoded_content = input_content.decode("utf-8")

        data_content = io.StringIO(decoded_content)

        reader = csv.DictReader(data_content)
        rows = list(reader)

        end = len(rows) if limit == 0 else start + limit
        piis = [row["PII"] for row in rows[start:end] if row["PII"]]

        # INSTANCIATE CRAWLER
        crawler_class = self._get_crawler(crawler_option)
        crawler = crawler_class()

        await crawler.download_all(piis)

    def _get_crawler(self, crawler_option: Literal["PLAYWRIGHT", "SELENIUM"]):
        if crawler_option == "PLAYWRIGHT":
            return PlayWrightCrawler

        elif crawler_option == "SELENIUM":
            return SeleniumCrawler
