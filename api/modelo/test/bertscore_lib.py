import pandas as pd
import re
from tqdm import tqdm
from transformers import BertTokenizer, BertModel
from bert_score import BERTScorer


class BertEvaluator:
    def score(self, reference, candidate):
        scorer = BERTScorer(model_type="bert-base-uncased")
        P, R, F1 = scorer.score([candidate], [reference])
        return P, R, F1


if __name__ == "__main__":
    bert_scorer = BertEvaluator()

    nome_base = None
    models = [
        #     "gpt-3.5-turbo",
        #     "llama-3.1-8b-instant",
        #     "llama-3.3-70b-versatile",
        #     "llama3-8b-8192",
        #     "llama3-70b-8192",
        #     "gpt-4",
        "RAG"
    ]

    for model in models:
        resultados: list = []
        path = f"./data/{model}_answers.csv"

        df = pd.read_csv(path)

        match = re.search(r"\./data/([a-zA-Z0-9\-_.]+)\.csv", path)

        if match:
            nome_base = match.group(1)
            print(nome_base)

        if nome_base:
            for _, row in tqdm(df.iterrows(), total=len(df)):
                if pd.isnull(row["Resposta_Gerada"]):
                    row["Resposta_Gerada"] = ""

                if pd.isnull(row["Pergunta"]) and pd.isnull(row["Resposta"]):
                    row["Pergunta"] = ""
                    row["Resposta"] = ""

                P, R, F1 = bert_scorer.score(row["Resposta_Gerada"], row["Resposta"])
                resultados.append(
                    {
                        "Pergunta": row["Pergunta"],
                        "Resposta_Esperada": row["Resposta"],
                        "Resposta_Gerada": row["Resposta_Gerada"],
                        "Precision": P,
                        "RECALL": R,
                        "F1-Score": F1,
                    }
                )

            pd.DataFrame(resultados).to_csv(f"./resultados/bertscore/{nome_base}.csv")
