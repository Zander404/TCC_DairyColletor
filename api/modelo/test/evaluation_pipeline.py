import csv
from pathlib import Path
from typing import Dict, List, Tuple

from pandas.core.algorithms import mode
from api.modelo.test.evaluators.bleuscore import BleuScore
from api.utils.save_csv import save_results_in_csv
import pandas as pd

from api.modelo.test.evaluators.bartscore import BARTScorer
from api.modelo.test.evaluators.base_evaluator import BaseEvaluator
from api.modelo.test.evaluators.bertscore import BertEvaluator
from api.modelo.test.evaluators.rougescore import RougeScorerEvaluator


def get_evaluator(name: str) -> BaseEvaluator:
    if name == "bleuscore":
        return BleuScore(weights=(0.25, 0.25, 0, 0))

    elif name == "bartscore":
        return BARTScorer()

    elif name == "bertscore":
        return BertEvaluator()

    elif name == "rougescore":
        return RougeScorerEvaluator()

    elif name == "gptscore":
        raise NotImplementedError("Modelo ainda não implementado")

    raise Exception(f" O Evaluator {name} informado não existe na lista.")


def evaluate_answers(
    evaluator: BaseEvaluator,
    evaluator_name: str,
    models: Tuple[str, ...],
    path_to_csv_model: Path = Path("api/modelo/test/data/"),
) -> None:
    # for model in models:
    #     resultados: List[Dict[str, str]] = []
    #
    #     try:
    #         df: pd.DataFrame = pd.read_csv(
    #             path_to_csv_model / str(model + "_answers.csv")
    #         )
    #
    #         resultados = evaluator.process_data_row(df)
    #         save_results_in_csv(evaluator_name, resultados, model)
    #         print(f"arquivo concluido {model}")
    #     except FileNotFoundError as e:
    #         print(f"O arquivo não foi encontrado {path_to_csv_model}: \n Erro: {e}")

    for model in path_to_csv_model.iterdir():
        df: pd.DataFrame = pd.DataFrame()
        try:
            print(model.suffix)
            if model.suffix == ".csv":
                df = pd.read_csv(path_to_csv_model / str(model.name))
                print("CSV")

            elif model.suffix == ".tsv":
                df = pd.read_csv(path_to_csv_model / str(model.name), sep="\t")
                df.rename(
                    columns={
                        "question": "Pergunta",
                        "base_answer": "Resposta",
                        "answer": "Resposta_Gerada",
                    },
                    inplace=True,
                )
                print(df.tail())

            resultados = evaluator.process_data_row(df)
            save_results_in_csv(evaluator_name, resultados, model.name)
            print(f"arquivo concluido {model}")
        except FileNotFoundError as e:
            print(f"O arquivo não foi encontrado {path_to_csv_model}: \n Erro: {e}")


if __name__ == "__main__":
    EVALUATORS_LIST: Tuple[str, ...] = (
        "bleuscore",
        "rougescore",
        "bartscore",
        "bertscore",
        # "gptscore",
    )

    MODELS: Tuple[str, ...] = (
        # "gpt-3.5-turbo",
        # "gpt-4",
        # "llama-3.1-8b-instant",
        # "llama-3.3-70b-versatile",
        # "llama3-8b-8192",
        # "llama3-70b-8192",
        # "rag_answers",
        # "qwen2",
        "llama3.1_rag",
    )

    for evaluator_name in EVALUATORS_LIST:
        model_evaluator: BaseEvaluator = get_evaluator(evaluator_name)
        evaluate_answers(
            model_evaluator,
            evaluator_name,
            MODELS,
        )
