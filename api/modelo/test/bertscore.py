import torch
from transformers import AutoTokenizer, AutoModel
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import pandas as pd
import re
from tqdm import tqdm


class BertEvaluator:
    def __init__(self, model_name="bert-base-multilingual-cased", device="cpu"):
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(model_name)
        self.device = torch.device(device if torch.cuda.is_available() else "cpu")
        self.model.to(self.device)
        self.model.eval()

    def _get_token_embeddings(self, text: str):
        encoded_input = self.tokenizer(
            text, return_tensors="pt", padding=True, truncation=True, max_length=512
        ).to(self.device)

        with torch.no_grad():
            output = self.model(**encoded_input)

        embeddings = output.last_hidden_state[0]
        tokens = self.tokenizer.convert_ids_to_tokens(encoded_input["input_ids"][0])

        start_index = 1  # ignora [CLS]
        end_index = len(tokens) - 1  # ignora [SEP]

        if "[PAD]" in tokens:
            end_index = tokens.index("[PAD]")

        return embeddings[start_index:end_index], tokens[start_index:end_index]

    def _calculate_bert_score(self, candidate_text, reference_text):
        cand_embeds, cand_tokens = self._get_token_embeddings(candidate_text)
        ref_embeds, ref_tokens = self._get_token_embeddings(reference_text)

        if not cand_tokens or not ref_tokens:
            return 0.0, 0.0, 0.0

        cand_np = cand_embeds.cpu().numpy()
        ref_np = ref_embeds.cpu().numpy()

        sim_matrix = cosine_similarity(cand_np, ref_np)

        precision = np.mean(np.max(sim_matrix, axis=1))
        recall = np.mean(np.max(sim_matrix, axis=0))
        f1 = (
            0.0
            if (precision + recall) == 0
            else 2 * (precision * recall) / (precision + recall)
        )

        return precision, recall, f1

    def score(self, candidates, references):
        precisions, recalls, f1_scores = [], [], []
        for cand, ref in zip(candidates, references):
            p, r, f = self._calculate_bert_score(cand, ref)
            precisions.append(p)
            recalls.append(r)
            f1_scores.append(f)

        return np.mean(precisions), np.mean(recalls), np.mean(f1_scores)


if __name__ == "__main__":
    bert_scorer = BertEvaluator(device="cuda")

    nome_base = None
    models = [
        # "gpt-3.5-turbo",
        # "gpt-4",
        # "llama-3.1-8b-instant",
        # "llama-3.3-70b-versatile",
        # "llama3-8b-8192",
        # "llama3-70b-8192",
        # "rag_answers",
        "qwen2"
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
