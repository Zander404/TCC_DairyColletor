from typing import Any, Dict
import pandas as pd


def normalize_row(row: pd.Series) -> pd.Series:
    if "Resposta_Gerada" in row and pd.isnull(row["Resposta_Gerada"]):
        row["Resposta_Gerada"] = ""

    if "Pergunta" in row and "Resposta" in row:
        if pd.isnull(row["Pergunta"]) and pd.isnull(row["Resposta"]):
            row["Pergunta"], row["Resposta"] = "", ""

    return row
