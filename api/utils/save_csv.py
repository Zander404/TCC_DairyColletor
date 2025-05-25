import os
import threading
import csv


csv_lock = threading.Lock()


def save_csv(filename: str, header: list[str], data: list) -> None:
    """
    Save the Info in a CSV file
    """
    with csv_lock:
        file_exists = os.path.exists(filename) and os.path.getsize(filename) > 0

        with open(filename, "a", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=header)

            if not file_exists:
                writer.writeheader()

            writer.writerows(data)
