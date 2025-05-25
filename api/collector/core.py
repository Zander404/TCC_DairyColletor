import asyncio
import os
import csv
import time
import threading
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor, as_completed, thread
import requests
from dotenv import load_dotenv


load_dotenv()

API_KEY = os.getenv("API_KEY")
# keywords_list = ["dairy", "dairy cows", "dairy farming", "dairies"]
keywords_list = ["Journal of dairy science"]
keywords = "+".join(keywords_list)
url_pubmed = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"

url_search = f"{url_pubmed}/esearch.fcgi?&api_key{API_KEY}&db=pubmed&retmode=json&term={
    keywords
}&retmax="

url_fetch: str = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?api_key={
    API_KEY
}&db=pubmed&rettype=abstract&id="

columns = [
    "PubMedID",
    "DOI",
    "URL",
    "Journal",
    "Title",
    "Abstract",
    "Author",
    "Year",
    "Keywords",
]


async def collect_articleID(
    start: int = 0, limit: int = 1000, step: int = 1000
) -> None:
    """
    Search in the PubMed API and get the articles about the keywords set in the path/router
    :params
    """
    count = start + step
    while True:
        data = requests.get(url_search + str(count))
        if data.status_code != 200 or count > limit:
            break

        count += step
        content = data.json()
        count_articles = content["esearchresult"]["count"]
        id_list = content["esearchresult"]["idlist"]

        existed_id: list[int] = pubmed_id_exist()

        with open("collect.csv", "w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=columns)

            if not os.path.exists("collect.csv") or os.path.getsize("collect.csv") == 0:
                writer.writeheader()

            for id_ in id_list:
                if int(id_) in existed_id:
                    continue

                row = {
                    "PubMedID": id_,
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

        time.sleep(1)


async def collect_abstract(
    start: int = 0, limit: int = 0, max_threads: int = 10
) -> None:
    """
    Function to get the abstract of all PubMedID articles register in the csv generate by the collect_articleID
    """

    with open("collect.csv", "r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        data = list(reader)
        if limit == 0:
            limit = len(data) - 1

        pub_med_data: list = [row for row in data if row["PubMedID"]][start:limit]

    results = []
    with ThreadPoolExecutor(max_workers=max_threads) as executor:
        futures = [executor.submit(extract_data, data) for data in pub_med_data]

        for future in as_completed(futures):
            data = future.result()
            if data:
                results.append(data)

    save_csv("test.csv", results)


def extract_data(row: dict) -> list:
    """
    Get the article information using a row with the Arcticle PUB_MED ID from CSV file  and retrive specified info like: TITLE, ABSTRACT and KEYWORDS
    """
    thread_name = threading.current_thread().name
    #  print(f"[{thread_name}] Processamento ID: {row['PubMedID']}")
    try:
        row["URL"] = f"{url_fetch}{str(row['PubMedID'])}"
        data = requests.get(row["URL"])
        content = data.text
        root = ET.fromstring(content)
        row["Journal"] = root.find(".//Title").text
        row["Title"] = root.find(".//ArticleTitle").text
        row["Abstract"] = " ".join(
            elem.text.strip() for elem in root.findall(".//AbstractText") if elem.text
        )
        row["Author"] = [
            f"{a.find('ForeName').text} {a.find('LastName').text}"
            for a in root.findall(".//Author")
        ]
        row["Year"] = f"{root.find('.//Day').text}-{root.find('.//Month').text}-{
            root.find('.//Year').text
        }"
        row["DOI"] = root.find(".//ELocationID[@EIdType='doi']").text
        row["Keywords"] = " ".join(
            elem.text.strip() for elem in root.findall(".//Keyword") if elem.text
        )
        time.sleep(1)
        return row

    except Exception as e:
        print(f"[{thread_name}] Erro com ID {row['PubMedID']}: {e}")
        return []


def pubmed_id_exist() -> list:
    """
    Generate a List with all PubMedID saved in the CSV file
    """
    if os.path.exists("collect.csv"):
        with open("collect.csv", "r") as file:
            reader = csv.DictReader(file)
            data = list(reader)
            row = [int(row["PubMedID"]) for row in data if row["PubMedID"]]

        return row

    return []


csv_lock = threading.Lock()


def save_csv(filename: str, data: list) -> None:
    """
    Save the Info in a CSV file
    """
    with csv_lock:
        file_exists = os.path.exists(filename) and os.path.getsize(filename) > 0

        with open(filename, "a", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=columns)

            if not file_exists:
                writer.writeheader()

            writer.writerows(data)


async def teste():
    await collect_articleID(limit=1000, step=1000)


if __name__ == "__main__":
    # print("Coletado IDS....")
    # asyncio.run(teste())

    # print("Coletando ABSTRACTS....")
    # collect_abstract(start=0, limit=1, max_threads=1)
    # print("TESTE DE EXTRACT DATA")
    data = extract_data(
        {"PubMedID": 40150329, "URL": "", "Title": "", "Abstract": "", "Keywords": ""}
    )
    print(data)
