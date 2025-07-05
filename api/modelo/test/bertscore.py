import torch
from transformers import AutoTokenizer, AutoModel
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import pandas as pd
import re
from tqdm import tqdm

class BertEvaluator():
    def __init__(self, model_name="bert-base-multilingual-cased", device="cpu"):

        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(model_name)
        self.device = torch.device(device if torch.cuda.is_available() else 'cpu')
        self.model.to(self.device)
        self.model.eval()



    def _get_token_embeddings(self, text: str):
        # Tokeniza o texto
        encoded_input = self.tokenizer(
            text,
            return_tensors='pt',
            padding=True,
            truncation=True,
            max_length=512
        ).to(self.device)

        with torch.no_grad(): # Desativa o cálculo de gradientes para otimização de memória e velocidade
            output = self.model(**encoded_input)

        embeddings = output.last_hidden_state[0]
        tokens = self.tokenizer.convert_ids_to_tokens(encoded_input['input_ids'][0])

        start_index = 1 # Ignora [CLS]
        end_index = len(tokens) - 1 # Ignora [SEP] (se não houver padding)
        
        if '[PAD]' in tokens:
            end_index = tokens.index('[PAD]')

        filtered_embeddings = embeddings[start_index:end_index]
        filtered_tokens = tokens[start_index:end_index]
        
        return filtered_embeddings, filtered_tokens

    def _calculate_bert_score(self, candidate_text, reference_text):
        candidate_embeddings, cand_tokens = self._get_token_embeddings(candidate_text)
        reference_embeddings, ref_tokens = self._get_token_embeddings(reference_text)

        if len(cand_tokens) == 0 or len(ref_tokens) == 0:
            # Caso algum texto seja vazio após a remoção de tokens especiais
            return 0.0, 0.0, 0.0

        # Converte para numpy para usar sklearn.metrics.pairwise.cosine_similarity
        cand_embeds_np = candidate_embeddings.cpu().numpy()
        ref_embeds_np = reference_embeddings.cpu().numpy()

        similarity_matrix = cosine_similarity(cand_embeds_np, ref_embeds_np)

        precision_scores = np.max(similarity_matrix, axis=1)
        precision = np.mean(precision_scores)

        recall_scores = np.max(similarity_matrix, axis=0)
        recall = np.mean(recall_scores)

        if precision + recall == 0:
            f1 = 0.0
        else:
            f1 = 2 * (precision * recall) / (precision + recall)

        return precision, recall, f1



    def score(self, candidates, references):

        precisions, recalls, f1_scores = [], [], []
        for cand, ref in zip(candidates, references):
            p, r, f1 = self._calculate_bert_score(cand, ref)
            precisions.append(p)
            recalls.append(r)
            f1_scores.append(f1)
        
        return np.array(precisions), np.array(recalls), np.array(f1_scores)



if __name__ == "__main__":
    bert_scorer = BertEvaluator(device="cuda")
  
    nome_base = None
    models = [
        "gpt-3.5-turbo",
        "llama-3.1-8b-instant",
        "llama-3.3-70b-versatile",
        "llama3-8b-8192",
        "llama3-70b-8192",
        "whisper-large-v3",
        "whisper-large-v3-turbo",
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
                if (
                    pd.isnull(row["Pergunta"])
                    or pd.isnull(row["Resposta"])
                    or pd.isnull(row["Resposta_Gerada"])
                ):
                    continue

                P, R, F1 = bert_scorer.score(row["Resposta_Gerada"], row["Resposta"])
                resultados.append(
                    {
                        "Pergunta": row["Pergunta"],
                        "Resposta_Esperada": row["Resposta"],
                        "Resposta_Gerada": row["Resposta_Gerada"],
                        "Precision": P,
                        "RECALL": R,
                        "F1-Score": F1
                    }
                )

            pd.DataFrame(resultados).to_csv(f"./resultados/bertscore/{nome_base}.csv")


