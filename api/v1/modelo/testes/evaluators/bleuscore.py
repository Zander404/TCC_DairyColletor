from api.modelo.test.evaluators.base_evaluator import BaseEvaluator
import nltk
from nltk.translate.bleu_score import sentence_bleu
import pandas as pd
from tqdm import tqdm

from typing import Any, List, Dict

from api.modelo.test.data_processing.normalizer import normalize_row

# nltk.download("punkt_tab")


class BleuScore(BaseEvaluator[list[int]]):
    def __init__(self, weights: tuple[float, float, float, float]):
        self.weights = weights

    def score(
        self, reference_text: pd.Series, prediction_text: pd.Series
    ) -> list[int] | Any:
        reference = [nltk.word_tokenize(reference_text)]
        prediction = nltk.word_tokenize(prediction_text)
        return sentence_bleu(reference, prediction, weights=self.weights)

    def process_data_row(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        results: List[Dict[str, Any]] = []

        for _, row in tqdm(df.iterrows(), total=len(df)):
            row: pd.Series = normalize_row(row)

            prediction: List[int] = self.score(
                prediction_text=row["Resposta_Gerada"],
                reference_text=row["Resposta"],
            )

            results.append(
                {
                    "Pergunta": row["Pergunta"],
                    "Resposta_Esperada": row["Resposta"],
                    "Resposta_Gerada": row["Resposta_Gerada"],
                    "Score": prediction,
                }
            )

        return results

    def test(self):
        reference = "the picture is clicked by me"

        predictions = "the picture the picture by me"

        result = self.score(reference, predictions)
        assert result == 0.7186082239261684
