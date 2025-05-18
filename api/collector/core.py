import os
import csv
import time
import xml.etree.ElementTree as ET

import requests
from dotenv import load_dotenv


load_dotenv()

API_KEY = os.getenv("API_KEY")
keywords_list = ["dairy"]
keywords = "+".join(keywords_list)
url_pubmed = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"

url_search = (
    f"{url_pubmed}/esearch.fcgi?&db=pubmed&retmode=json&term={keywords}&retmax="
)

url_fetch: str = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&rettype=abstract&id="

columns = ["PubMedID", "URL", "Title", "Abstract", "Keywords"]


def collect_articleID(start: int = 0, limit: int = 1000, step: int = 1000) -> None:
    count = start
    while True:
        data = requests.get(url_search + str(count))
        if data.status_code != 200 or count >= limit:
            break

        count += step
        content = data.json()
        count_articles = content["esearchresult"]["count"]
        id_list = content["esearchresult"]["idlist"]

        existed_id: list[int] = pubmed_id_exist()

        with open("collect.csv", "a+", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=columns)
            if not os.path.exists("collect.csv") or os.path.getsize("collect.csv") == 0:
                writer.writeheader()

            for id_ in id_list:
                if int(id_) in existed_id:
                    continue
                row = {"PubMedID": id_, "URL": "", "Title": "", "Abstract": ""}
                writer.writerow(row)

        time.sleep(1)


def collect_abstract(limit: int = 0, start: int = 0) -> None:
    with open("collect.csv", "r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        data = list(reader)
        if limit == 0:
            limit = len(data) - 1

        pub_med_data: list = [row for row in data if row["PubMedID"]][start:limit]

        extract_data_from_collection(pub_med_data)


def extract_data_from_collection(collection: list) -> None:
    cache_abstract = []

    for i, row in enumerate(collection):
        row["URL"] = f" {url_fetch}{str(row['PubMedID'])}"
        data = requests.get(row["URL"])
        content = data.text
        root = ET.fromstring(content)
        row["Title"] = root.find(".//Title").text
        row["Abstract"] = " ".join(
            elem.text.strip() for elem in root.findall(".//AbstractText") if elem.text
        )
        row["Keywords"] = " ".join(
            elem.text.strip() for elem in root.findall(".//Keyword") if elem.text
        )

        cache_abstract.append(row)

        time.sleep(1)

        if i % 100 == 0:
            save_csv("collect_data.csv", cache_abstract)
            print(f"Saved in  iteration number {i}")
            cache_abstract.clear()


def pubmed_id_exist() -> list:
    if os.path.exists("collect.csv"):
        with open("collect.csv", "r") as file:
            reader = csv.DictReader(file)
            data = list(reader)
            row = [int(row["PubMedID"]) for row in data if row["PubMedID"]]

        return row

    return []


def save_csv(filename: str, data: list) -> None:
    with open(filename, "a+", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=columns)
        if not os.path.exists(filename) or os.path.getsize(filename) == 0:
            writer.writeheader()

        writer.writerows(data)


if __name__ == "__main__":
    print("Coletado IDS....")
    collect_articleID(limit=1000)
    print("Coletando ABSTRACTS....")
    collect_abstract()
