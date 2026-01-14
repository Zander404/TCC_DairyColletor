import csv
import os
import threading
from typing import Dict, List
import xml.etree.ElementTree as ET

import requests

# from api.collector.core.util import pubmed_id_exist, save_csv
from api.collector.utils.constants import COLUMNS, URL_SEARCH
from api.collector.utils.constants import URL_FETCH


class PubMedClient:
    def __init__(
        self,
        url_search: str = URL_SEARCH,
        columns: List[str] = COLUMNS,
        max_threads: int = 10,
    ):
        self.url_search = url_search
        self.columns = columns
        self.max_threads = max_threads

    def colect_articleID(
        self, input_file: str, start: int = 0, limit: int = 1000, step: int = 1000
    ) -> None:
        """
        Search in the PubMed API and get the articles about the keywords set in the
        path/router and Save in a CSV

        Args:

            input_file: The name of file to save all Article ID's

            start: Start Value to collect the Article ID's
            limit: Limit to make the collect of Article ID's
            step : Offset to jump between Articles


        Returns:
            None
        """

        count: int = start + step
        while True:
            data = requests.get(self.url_search + str(count))
            if data.status_code != 200 or count > limit:
                break

            count += step
            content: str = data.json()
            count_articles = content["esearchresult"]["count"]
            print(count_articles)
            id_list = content["esearchresult"]["idlist"]

            existed_id: list[int] = pubmed_id_exist(input_file)

            with open(input_file, "w", newline="", encoding="utf-8") as file:
                writer = csv.DictWriter(file, fieldnames=COLUMNS)

                if not os.path.exists(input_file) or os.path.getsize(input_file) == 0:
                    writer.writeheader()

                for id_ in id_list:
                    if int(id_) in existed_id:
                        continue

                    row = {column: "" for column in self.columns}
                    row["PubMedID"] = ""

                    writer.writerow(row)

    async def collect_abstract(
        self, input_file: str, output_file: str, start: int = 0, limit: int = 0
    ) -> None:
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

        with open(input_file, "r", encoding="utf-8") as file:
            reader = csv.DictReader(file)
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

            save_csv(output_file, results)

    def extract_data(self, row: dict) -> Dict[str, str]:
        """
        Get the article information using a row with the Arcticle PUB_MED ID from CSV file  and retrive specified info like: TITLE, ABSTRACT and KEYWORDS
        """
        thread_name = threading.current_thread().name
        #  print(f"[{thread_name}] Processamento ID: {row['PubMedID']}")
        try:
            row["URL"] = f"{URL_FETCH}{str(row['PubMedID'])}"
            data = requests.get(row["URL"])
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
            row["Year"] = f"{root.find('.//Day').text}-{root.find('.//Month').text}-{
                root.find('.//Year').text
            }"
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
    colector.colect_articleID(input_file=test_input_file)
