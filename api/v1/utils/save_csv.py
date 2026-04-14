import os
from os.path import exists
from pathlib import Path
import threading
import csv
from typing import Any, Dict, List
import pandas as pd


csv_lock = threading.Lock()


def save_csv(
    filename: str, header: list[str], data: list, save_type: str = "w"
) -> None:
    """
    Save the Info in a CSV file
    """
    with csv_lock:
        file_exists = os.path.exists(filename) and os.path.getsize(filename) > 0

        with open(filename, save_type, newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=header)
            writer.writeheader()

            writer.writerows(data)


def save_results_in_csv(
    evaluator_name: str, results: List[Dict[str, Any]], model_name: str
) -> None:
    """
    Salvar os resultados em um CSV no diretorio informado

    Args:
        evaluator_name: Nome do Avaliado (Evaluator) utilizado
        results: Lista de dicionarios contendo os dados a serem salvos
        model_name: Nome do Modelo que foi Avaliado
    """

    evaluator_path: Path = Path(f"api/modelo/test/data/resultados/{evaluator_name}/")

    evaluator_path.mkdir(parents=True, exist_ok=True)
    df_results: pd.DataFrame = pd.DataFrame(results)
    df_results.to_csv(
        evaluator_path / f"{model_name}_{evaluator_name}.csv", index=False
    )
