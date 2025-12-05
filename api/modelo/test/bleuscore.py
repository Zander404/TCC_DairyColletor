import nltk
from nltk.translate.bleu_score import corpus_bleu, sentence_bleu
from pydantic_core.core_schema import list_schema

nltk.download("punkt_tab")


class BleuScore:
    def __init__(self, weights: tuple[float, float, float, float]):
        self.weights = weights

    def score(self, reference_text: str, prediction_text: str):
        reference = [nltk.word_tokenize(reference_text)]
        prediction = nltk.word_tokenize(prediction_text)
        return sentence_bleu(reference, prediction, weights=self.weights)

    def test(self):
        reference = "the picture is clicked by me"

        predictions = "the picture the picture by me"

        result = self.score(reference, predictions)
        assert result == 0.7186082239261684


if __name__ == "__main__":
    import pandas as pd
    from tqdm import tqdm
    import re

    blue_score = BleuScore(weights=(0.25, 0.25, 0, 0))

    models = [
        # "gpt-3.5-turbo",
        # "llama-3.1-8b-instant",
        # "llama-3.3-70b-versatile",
        # "llama3-8b-8192",
        # "llama3-70b-8192",
        # "gpt-4",
        "RAG"
    ]

    for model in models:
        resultados = []
        path = f"./data/{model}_answers.csv"
        df = pd.read_csv(path)

        nome_base = None

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

                evaluation = blue_score.score(
                    prediction_text=row["Resposta_Gerada"],
                    reference_text=row["Resposta"],
                )

                resultados.append(
                    {
                        "Pergunta": row["Pergunta"],
                        "Resposta_Esperada": row["Resposta"],
                        "Resposta_Gerada": row["Resposta_Gerada"],
                        "Score": evaluation,
                    }
                )

            pd.DataFrame(resultados).to_csv(
                f"./resultados/bleu/{nome_base}.csv")
