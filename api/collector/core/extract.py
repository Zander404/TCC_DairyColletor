import threading
from typing import Dict
import xml.etree.ElementTree as ET
import requests

from api.collector.utils.constants import URL_FETCH


def extract_data(row: dict) -> Dict[str, str]:
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
        row["PII"] = root.find(".//ELocationID[@EIdType='pii']").text
        row["Keywords"] = " ".join(
            elem.text.strip() for elem in root.findall(".//Keyword") if elem.text
        )
        # time.sleep(1)
        return row

    except Exception as e:
        print(f"[{thread_name}] Erro com ID {row['PubMedID']}: {e}")
        return dict()
