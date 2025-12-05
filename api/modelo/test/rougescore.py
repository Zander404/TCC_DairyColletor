from rouge_score import rouge_scorer
import rouge_score


class RougeScorerEvaluator:
    def __init__(self):
        self.scorer = rouge_scorer.RougeScorer(
            ["rouge1", "rouge2", "rougeL"], use_stemmer=True
        )

    def score(self, reference, hypothesis):
        scores = self.scorer.score(reference, hypothesis)

        return {
            "ROUGE-1": scores["rouge1"].fmeasure,
            "ROUGE-2": scores["rouge2"].fmeasure,
            "ROUGE-L": scores["rougeL"].fmeasure,
        }


def teste():
    reference = "Photosynthesis is the process by which plants convert sunlight into chemical energy."
    hypothesis = "Plants use sunlight to make energy, a process called photosynthesis."

    rouge_evaluator = RougeScorerEvaluator()

    test = rouge_evaluator.score(reference, hypothesis)
    for metric, score in test.items():
        print(f"{metric}:  {score:.4f}")


if __name__ == "__main__":
    import pandas as pd
    from tqdm import tqdm
    import re

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

        rouge_evaluator = RougeScorerEvaluator()

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

                evaluation = rouge_evaluator.score(
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

            pd.DataFrame(resultados).to_csv(f"./resultados/rouge/{nome_base}.csv")
