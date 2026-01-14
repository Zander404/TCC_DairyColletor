from rouge_score import rouge_scorer

from api.modelo.test.data_processing.normalizer import normalize_row
from typing import Any, List, Dict
import pandas as pd
from tqdm import tqdm
from api.modelo.test.evaluators.base_evaluator import BaseEvaluator


class RougeScorerEvaluator(BaseEvaluator[Dict[str, str]]):
    def __init__(self):
        self.scorer = rouge_scorer.RougeScorer(
            ["rouge1", "rouge2", "rougeL"], use_stemmer=True
        )

    def score(self, reference, hypothesis) -> Dict[str, str]:
        scores = self.scorer.score(reference, hypothesis)

        return {
            "ROUGE-1": scores["rouge1"].fmeasure,
            "ROUGE-2": scores["rouge2"].fmeasure,
            "ROUGE-L": scores["rougeL"].fmeasure,
        }

    def test(self):
        reference = "Photosynthesis is the process by which plants convert sunlight into chemical energy."
        hypothesis = (
            "Plants use sunlight to make energy, a process called photosynthesis."
        )

        test = self.score(reference, hypothesis)
        for metric, score in test.items():
            print(f"{metric}:  {score:.4f}")

    def process_data_row(self, dataframe: pd.DataFrame) -> List[Dict[str, Any]]:
        resultados: List[Dict[str, Any]] = []
        for _, row in tqdm(dataframe.iterrows(), total=len(dataframe)):
            row = normalize_row(row)

            evaluation = self.score(
                hypothesis=row["Resposta_Gerada"], reference=row["Resposta"]
            )

            resultados.append(
                {
                    "Pergunta": row["Pergunta"],
                    "Resposta_Esperada": row["Resposta"],
                    "Resposta_Gerada": row["Resposta_Gerada"],
                    "ROUGE1": evaluation["ROUGE-1"],
                    "ROUGE2": evaluation["ROUGE-2"],
                    "ROUGEL": evaluation["ROUGE-L"],
                }
            )

        return resultados
