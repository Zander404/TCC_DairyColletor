import pandas as pd
from tqdm import tqdm
from bert_score import BERTScorer

from api.modelo.test.data_processing.normalizer import normalize_row

from typing import List, Any, Dict, Tuple

from api.modelo.test.evaluators.base_evaluator import BaseEvaluator


class BertEvaluator(BaseEvaluator[Tuple[float, float, float]]):
    def score(self, reference: str, candidate: str) -> Tuple[float, float, float]:
        scorer = BERTScorer(model_type="bert-base-uncased")
        P, R, F1 = scorer.score([candidate], [reference])
        return P.item(), R.item(), F1.item()

    def process_data_row(self, dataframe: pd.DataFrame) -> List[Dict[str, Any]]:
        processed_data: List[Dict[str, Any]] = []

        for _, row in tqdm(dataframe.iterrows(), total=len(dataframe)):
            ### Normalizar a Linha
            row = normalize_row(row)

            P, R, F1 = self.score(row["Resposta_Gerada"], row["Resposta"])

            processed_data.append(
                {
                    "Pergunta": row["Pergunta"],
                    "Resposta_Esperada": row["Resposta"],
                    "Resposta_Gerada": row["Resposta_Gerada"],
                    "Precision": P,
                    "RECALL": R,
                    "F1-Score": F1,
                }
            )

        return processed_data

    def test(self) -> None:
        reference = "the picture is clicked by me"

        predictions = "the picture the picture by me"

        result = self.score(reference, predictions)

        # FIX: Verificar o resultado para esse caso

        assert result == 0.7186082239261684
