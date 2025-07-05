from transformers import BartTokenizer, BartForConditionalGeneration
import torch


class BartEvaluator:
    def __init__(self, device="cpu"):
        self.tokenizer = BartTokenizer.from_pretrained("facebook/bart-large-cnn")
        self.model = BartForConditionalGeneration.from_pretrained(
            "facebook/bart-large-cnn"
        ).to(device)
        self.model.eval()

    def score(self, reference, hypothesis, normalize=True):
        input_ids = self.tokenizer(reference, max_length=1024, truncation=True, return_tensors="pt").input_ids.to(
            self.model.device
        )
        with self.tokenizer.as_target_tokenizer():
            labels = self.tokenizer(hypothesis, max_length=1024, truncation=True, return_tensors="pt").input_ids.to(
                self.model.device
            )

        with torch.no_grad():
            loss = self.model(input_ids=input_ids, labels=labels).loss

        if normalize:
            return -loss.item()

        else:
            return -(loss.item() * labels.size(1))




if __name__ == "__main__":
    import pandas as pd
    from tqdm import tqdm
    import re

    bart_score = BartEvaluator()

    nome_base = None
    # models = [
    #     "gpt-3.5-turbo",
    #     "llama-3.1-8b-instant",
    #     "llama-3.3-70b-versatile",
    #     "llama3-8b-8192",
    #     "llama3-70b-8192",
    #     "whisper-large-v3",
    #     "whisper-large-v3-turbo",
    #
    # ]
    #
    models = [
        "llama-3.3-70b-versatile",
        "llama3-8b-8192",
        "llama3-70b-8192",

    ]


    for model in models:
        resultados = []
        path = f"./data/{model}_answers.csv"

        df = pd.read_csv(path)

        match = re.search(r"\./data/([a-zA-Z0-9\-_.]+)\.csv", path)

        if match:
            nome_base = match.group(1)
            print(nome_base)

        if nome_base:
            for _, row in tqdm(df.iterrows(), total=len(df)):
                if (
                    pd.isnull(row["Pergunta"])
                    or pd.isnull(row["Resposta"])
                    or pd.isnull(row["Resposta_Gerada"])
                ):
                    continue

                evaluation = bart_score.score(
                    hypothesis=row["Resposta_Gerada"], reference=row["Resposta"]
                )

                resultados.append(
                    {
                        "Pergunta": row["Pergunta"],
                        "Resposta_Esperada": row["Resposta"],
                        "Resposta_Gerada": row["Resposta_Gerada"],
                        "Score": evaluation,
                    }
                )

            pd.DataFrame(resultados).to_csv(f"./resultados/bartscore/{nome_base}.csv")
