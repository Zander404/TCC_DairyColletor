import os
from pathlib import Path
import pickle
import sys

import pandas as pd
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
    if text.strip()[-1] != ".":
        text = text.strip() + " ."
    new_text = text
    return new_text


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


def convert_csv_to_pkl(input_file: Path, output_path: Path) -> None:
    sep: str = "\t" if input_file.suffix == ".tsv" else ","
    file_name: str = input_file.stem

    df: pd.DataFrame = pd.read_csv(input_file, sep=sep)
    df_mapped = None

    if sep == "\t":
        df_mapped = df[["base_answer", "answer", "question"]]
        df_mapped.columns = ["ref_summs", "sys_summ", "question"]

    elif sep == ",":
        df_mapped = df[["base_answer", "answer", "question"]]
        df_mapped.columns = ["ref_summ", "sys_summ", "question"]

    data_list = df_mapped.to_dict(orient="records")

    with open(f"{output_path / file_name}.pkl", "wb") as f:
        pickle.dump(data_list, f)

    print("O arquivo foi salvo")


if __name__ == "__main__":
    input_file: Path = Path("./datas/500perguntasgadoleite.naive_rag.GRAG.tsv")
    output_path: Path = Path("./datas/")

    convert_csv_to_pkl(input_file, output_path)
