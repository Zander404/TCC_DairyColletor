import csv
import os
import threading

from api.collector.utils.constants import COLUMNS


def pubmed_id_exist(input_file: str) -> list:
    """
    Generate a List with all PubMedID saved in the CSV file

    Args:
        input_file: File to read all Articles ID's
    """
    if check_file_exists(file_path=input_file):
        with open(input_file, "r") as file:
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
        file_exists = os.path.exists(
            filename) and os.path.getsize(filename) > 0

        with open(filename, "a", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=COLUMNS)

            if not file_exists:
                writer.writeheader()

            writer.writerows(data)


def check_file_exists(file_path: str) -> bool:
    """
    Check if a certain file_path exists and not empty

    Args:
        file_path: Name/Path of the file to check if his null or not

    Return:
        True: His Exist and Has Data
        False: Don't Exist or Don't have Data to Use
    """

    if os.path.exists(file_path) or os.path.getsize(file_path) == 0:
        return False

    return True
