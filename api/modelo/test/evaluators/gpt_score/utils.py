from pathlib import Path
from typing import List
from nltk.lm import models
import pandas as pd


import os
import pickle
import sys

import nltk
from mosestokenizer import *
from nltk import word_tokenize
from nltk.tokenize import sent_tokenize
import json

nltk.download("stopwords")
detokenizer = MosesDetokenizer("en")


def read_demos(json_path):
    asp_demos = json.load(open(json_path))
    asp_dfs, demos = asp_demos["asp_definition"], asp_demos["demo"]
    return demos, asp_dfs


def lower_check(text):
    # The BAGEL dataset uses X to replace named entities.
    if text.startswith("X ") == False:
        text1 = text[0].lower() + text[1:]
    else:
        text1 = text
    return text1


def add_dot(text):
    # Verifica se o texto existe e não é apenas espaços
    if not text or not text.strip():
        return "."  # Ou return text, dependendo se você quer manter vazio

    if text.strip()[-1] != ".":
        return text.strip() + "."
    return text.strip()


def str2bool(v):
    if v.lower() in ("yes", "true", "t", "y", "1"):
        return True
    elif v.lower() in ("no", "false", "f", "n", "0"):
        return False
    else:
        raise argparse.ArgumentTypeError("Boolean value expected.")


def read_pickle(file):
    with open(file, "rb") as f:
        data = pickle.load(f)
    return data


def save_pickle(data, file):
    with open(file, "wb") as f:
        pickle.dump(data, f)
    print(f"Saved to {file}.")


def detokenize(text: str):
    words = text.split(" ")
    return detokenizer(words)


# Restore print
def enablePrint():
    sys.stdout = sys.__stdout__


def convert_csv_to_json(base_path: Path, file_name: Path) -> None:
    print(f"Convertendo o arquivo {file_name}.")
    output_path: Path = base_path / file_name.stem

    output_file: Path = output_path / "data.pkl"

    output_path.mkdir(parents=True, exist_ok=True)

    delimiter: str = "\t" if file_name.suffix == ".tsv" else ","
    df = pd.read_csv(file_name, delimiter=delimiter)

    columns: List[str] = [
        "src",
        "ref_summs",
        "sys_summ",
        "aspect",
        "polarity",
        "sys_name",
    ]

    if delimiter == "\t":
        df = df.rename(
            columns={
                "question": "src",
                "base_answer": "ref_summs",
                "answer": "sys_summ",
            }
        )

    elif delimiter == ",":
        df = df.rename(
            columns={
                "Pergunta": "src",
                "Resposta": "ref_summs",
                "Resposta_Gerada": "sys_summ",
            }
        )

    df["aspect"] = "informativeness"
    df["polarity"] = "positive"
    df["sys_name"] = file_name.stem
    df["sys_summ"] = (
        df["sys_summ"].fillna("").apply(lambda text: text.replace("\n", " ").strip())
    )
    df["ref_summs"] = (
        df["ref_summs"]
        .fillna("")
        .apply(
            lambda text: [text.replace("\n", " ").strip()]
            if isinstance(text, str)
            else text.replace("\n", " ").strip()
        )
    )
    df = df[columns]

    data_list = df.to_dict(orient="records")  # Transforma em lista de dicionários
    with open(output_file, "wb") as f:
        pickle.dump(data_list, f)

    df.to_json(
        f"{output_path / file_name.name}.json",
        orient="records",
        force_ascii=False,
        indent=4,
    )

    demo_path = base_path / "demos" / "d2t"
    with open(f"{demo_path}/{file_name.stem}_demos.json", "w") as f:
        json.dump(
            {
                "asp_definition": {"informativeness": ""},
                "demo": {"informativeness": []},
            },
            f,
        )


def convert_json_to_csv(json_file: Path):
    df_json = pd.read_json(json_file)

    df_json = df_json.T

    output_path = json_file.with_suffix(".csv")
    df_json.to_csv(output_path, index=True)


if __name__ == "__main__":
    base_path: Path = Path("./datas/")
    models = [
        "gpt-oss_com_5_docs",
        "gpt-oss_com_15_docs",
        "lllama3.1-naive_com_5_docs",
        "lllama3.1-naive_com_10_docs",
        "lllama3.1-naive_com_15_docs",
        "gpt-oss_com_10_docs",
    ]

    for file in base_path.iterdir():
        if file.is_file():
            models.append(file.stem)
            convert_csv_to_json(base_path, file)

    print(models)
    # base_results_dir: Path = Path("./analysis/d2t/")
    # base_pkl_dir: Path = Path("./datas/")
    #
    # try:
    #     for json in base_results_dir.rglob("*.json"):
    #         convert_json_to_csv(json)
    #         print("Conversão finalizada")
    #
    # except Exception as e:
    #     print(e)
