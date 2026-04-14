import csv
import os
from pathlib import Path
import re
import threading

from api.v1.collector.utils.constants import COLUMNS


def pubmed_id_exist(id_filepath: Path) -> list:
    """
    Generate a List with all PubMedID saved in the CSV file

    Args:
        input_file: File to read all Articles ID's
    """
    if id_filepath.exists():
        with open(id_filepath, "r") as file:
            reader = csv.DictReader(file)
            data = list(reader)
            row = [int(row["PubMedID"]) for row in data if row["PubMedID"]]

        return row

    return []


def save_csv(filename: str, data: list) -> None:
    """
    Save the Info in a CSV file
    """
    csv_lock = threading.Lock()

    with csv_lock:
        file_exists = os.path.exists(filename) and os.path.getsize(filename) > 0

        with open(filename, "a", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=COLUMNS)

            if not file_exists:
                writer.writeheader()

            writer.writerows(data)


def check_file_exists(filepath: Path) -> bool:
    """
    Check if a certain file_path exists and not empty

    Args:
        file_path: Name/Path of the file to check if his null or not

    Return:
        True: His Exist and Has Data
        False: Don't Exist or Don't have Data to Use
    """

    if not filepath.exists():
        return False

    return True


def mask_api_key(url: str, show: bool = False) -> str:
    if not show:
        return re.sub(r"(api_key=)[^&]+", r"\1****", url)

    return url
