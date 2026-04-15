import asyncio
import csv
import io
import logging
import os
from pathlib import Path
import threading
from typing import Dict, List
import xml.etree.ElementTree as ET

from fastapi import UploadFile
import requests
import pandas as pd

from api.v1.collector.utils.constants import (
    API_KEY,
    COLUMNS,
    PATH_COLLECTOR,
    URL_SEARCH,
)
from api.v1.collector.utils.constants import URL_FETCH
from api.v1.collector.utils.util import mask_api_key, pubmed_id_exist
from api.v1.utils.save_csv import save_csv


logger = logging.getLogger(__name__)


class PubMedClient:
    def __init__(
        self,
        url_search: str = URL_SEARCH,
        columns: List[str] = COLUMNS,
        max_threads: int = 10,
    ):
        self._data_path = PATH_COLLECTOR / "data"
        self.url_search = url_search
        self.columns = columns
        self.max_threads = max_threads

    async def colect_articleID(
        self, input_file: str, start: int = 0, limit: int = 1000, step: int = 1000
    ) -> pd.DataFrame | None:
        """
        Search in the PubMed API and get the articles about the keywords set in the
        path/router and Save in a CSV

        Args:

            input_file: The name of file to save all Article ID's

            start: Start Value to collect the Article ID's
            limit: Limit to make the collect of Article ID's
            step : Offset to jump between Articles


        Returns:
            pd.DataFrame
        """

        count: int = start + step
        try:
            data_list: List = []

            while True:
                data = requests.get(self.url_search + str(count))

                print(API_KEY)
                print(data.content)
                if count > limit:
                    break

                count += step
                content: str = data.json()
                count_articles = content["esearchresult"]["count"]
                logger.info(f"Contagem de artigos {count_articles}")
                id_list = content["esearchresult"]["idlist"]

                existed_id: list[int] = pubmed_id_exist(self._data_path / input_file)

                for id in id_list:
                    if int(id) in existed_id:
                        continue

                    row = {column: "" for column in self.columns}
                    row["PubMedID"] = id
                    data_list.append(row)

                df_data = pd.DataFrame(data_list)
                return df_data

        except Exception as e:
            raise Exception(f"Falha ao Coletar os ID. ERRO: {e}")

    async def collect_abstract(
        self,
        input_file: UploadFile,
        start: int = 0,
        limit: int = 1000,
    ) -> pd.DataFrame | None:
        """
        Function to get the abstract of all PubMedID articles register in the csv generate by the collect_articleID

        Args:
            input_file: Name of the CSV file to get the link and extract the Abstract from text
            output_file: Name to generate CSV with the Processed Result

            start: Number of Start Article
            limit: Number of Max Article to extract

            max_threads: Number of Max threads to using to process

        Returns:
            None
        """

        from concurrent.futures import ThreadPoolExecutor, as_completed

        try:
            contents = await input_file.read()

            decoder = contents.decode("utf-8")
            reader = csv.DictReader(io.StringIO(decoder))

            content: List[Dict[str, str]] = list(reader)

            if limit == 0:
                limit = len(content) - 1

            pub_med_data: List = [row for row in content if row["PubMedID"]][
                start:limit
            ]

            results = []

            with ThreadPoolExecutor(max_workers=self.max_threads) as executor:
                threads = [
                    executor.submit(self.extract_data, data) for data in pub_med_data
                ]

                for thread in as_completed(threads):
                    data = thread.result()

                    if data:
                        results.append(data)

                return pd.DataFrame(data=results, columns=COLUMNS)

        except Exception as e:
            raise Exception(f"Falha ao fazer a coleta dos abstracts. Erro: {e}")

    def extract_data(self, row: dict) -> Dict[str, str]:
        """
        Get the article information using a row with the Arcticle PUB_MED ID from CSV file  and retrive specified info like: TITLE, ABSTRACT and KEYWORDS
        """
        thread_name = threading.current_thread().name
        #  print(f"[{thread_name}] Processamento ID: {row['PubMedID']}")
        try:
            url_path: str = f"{URL_FETCH}{str(row['PubMedID'])}"
            data = requests.get(url_path)

            row["URL"] = mask_api_key(url_path, show=True)
            content = data.text
            root = ET.fromstring(content)
            row["Journal"] = root.find(".//Title").text
            row["Title"] = root.find(".//ArticleTitle").text
            row["Abstract"] = " ".join(
                elem.text.strip()
                for elem in root.findall(".//AbstractText")
                if elem.text
            )
            row["Author"] = [
                f"{a.find('ForeName').text} {a.find('LastName').text}"
                for a in root.findall(".//Author")
            ]
            row["Year"] = (
                f"{root.find('.//Day').text}-{root.find('.//Month').text}-{root.find('.//Year').text}"
            )
            row["DOI"] = root.find(".//ELocationID[@EIdType='doi']").text
            row["PII"] = root.find(".//ELocationID[@EIdType='pii']").text
            row["Keywords"] = " ".join(
                elem.text.strip() for elem in root.findall(".//Keyword") if elem.text
            )
            # time.sleep(1)
            return row

        except Exception as e:
            print(f"[{thread_name}] Erro com ID {row['PubMedID']}: {e}")
            return dict()


if __name__ == "__main__":
    test_input_file: str = "../../../500perguntasgadoleite.csv"
    colector = PubMedClient()
    asyncio.run(colector.colect_articleID(input_file=test_input_file))
