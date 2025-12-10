import csv
import requests
import os

from api.collector.core.util import pubmed_id_exist, save_csv
from api.collector.utils.constants import COLUMNS, URL_SEARCH
from api.collector.core.extract import extract_data


def collect_articleID(
    input_file: str,
    start: int = 0,
    limit: int = 1000,
    step: int = 1000,
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

    count = start + step

    while True:
        data = requests.get(URL_SEARCH + str(count))
        if data.status_code != 200 or count > limit:
            break

        count += step
        content = data.json()
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

                row = {
                    "PubMedID": id_,
                    "PII": "",
                    "DOI": "",
                    "URL": "",
                    "Journal": "",
                    "Title": "",
                    "Abstract": "",
                    "Author": "",
                    "Year": "",
                    "Keywords": "",
                }
                writer.writerow(row)


async def collect_abstract(
    input_file: str,
    output_file: str,
    start: int = 0,
    limit: int = 0,
    max_threads: int = 10,
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
        data = list(reader)
        if limit == 0:
            limit = len(data) - 1

        pub_med_data: list = [
            row for row in data if row["PubMedID"]][start:limit]

    results = []
    with ThreadPoolExecutor(max_workers=max_threads) as executor:
        futures = [executor.submit(extract_data, data)
                   for data in pub_med_data]

        for future in as_completed(futures):
            data = future.result()
            if data:
                results.append(data)

    save_csv(output_file, results)
