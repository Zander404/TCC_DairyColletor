import torch
import torch.nn as nn
import traceback
from transformers import BartTokenizer, BartForConditionalGeneration
from typing import List
import numpy as np


class BARTScorer:
    def __init__(
        self, device="cuda:0", max_length=1024, checkpoint="facebook/bart-large-cnn"
    ):
        # Set up model
        self.device = device
        self.max_length = max_length
        self.tokenizer = BartTokenizer.from_pretrained(checkpoint)
        self.model = BartForConditionalGeneration.from_pretrained(checkpoint)
        self.model.eval()
        self.model.to(device)

        # Set up loss
        self.loss_fct = nn.NLLLoss(
            reduction="none", ignore_index=self.model.config.pad_token_id
        )
        self.lsm = nn.LogSoftmax(dim=1)

    def load(self, path=None):
        """Load model from paraphrase finetuning"""
        if path is None:
            path = "models/bart.pth"
        self.model.load_state_dict(torch.load(path, map_location=self.device))

    def score(self, srcs, tgts, batch_size=4):
        """Score a batch of examples"""
        score_list = []
        for i in range(0, len(srcs), batch_size):
            src_list = srcs[i: i + batch_size]
            tgt_list = tgts[i: i + batch_size]
            try:
                with torch.no_grad():
                    encoded_src = self.tokenizer(
                        src_list,
                        max_length=self.max_length,
                        truncation=True,
                        padding=True,
                        return_tensors="pt",
                    )
                    encoded_tgt = self.tokenizer(
                        tgt_list,
                        max_length=self.max_length,
                        truncation=True,
                        padding=True,
                        return_tensors="pt",
                    )
                    src_tokens = encoded_src["input_ids"].to(self.device)
                    src_mask = encoded_src["attention_mask"].to(self.device)

                    tgt_tokens = encoded_tgt["input_ids"].to(self.device)
                    tgt_mask = encoded_tgt["attention_mask"]
                    tgt_len = tgt_mask.sum(dim=1).to(self.device)

                    output = self.model(
                        input_ids=src_tokens, attention_mask=src_mask, labels=tgt_tokens
                    )
                    logits = output.logits.view(-1,
                                                self.model.config.vocab_size)
                    loss = self.loss_fct(self.lsm(logits), tgt_tokens.view(-1))
                    loss = loss.view(tgt_tokens.shape[0], -1)
                    loss = loss.sum(dim=1) / tgt_len
                    curr_score_list = [-x.item() for x in loss]
                    score_list += curr_score_list

            except RuntimeError:
                traceback.print_exc()
                print(f"source: {src_list}")
                print(f"target: {tgt_list}")
                exit(0)
        return score_list

    def multi_ref_score(self, srcs, tgts: List[List[str]], agg="mean", batch_size=4):
        # Assert we have the same number of references
        ref_nums = [len(x) for x in tgts]
        if len(set(ref_nums)) > 1:
            raise Exception(
                "You have different number of references per test sample.")

        ref_num = len(tgts[0])
        score_matrix = []
        for i in range(ref_num):
            curr_tgts = [x[i] for x in tgts]
            scores = self.score(srcs, curr_tgts, batch_size)
            score_matrix.append(scores)
        if agg == "mean":
            score_list = np.mean(score_matrix, axis=0)
        elif agg == "max":
            score_list = np.max(score_matrix, axis=0)
        else:
            raise NotImplementedError
        return list(score_list)

    def test(self, batch_size=3):
        """Test"""
        src_list = [
            "This is a very good idea. Although simple, but very insightful.",
            "Can I take a look?",
            "Do not trust him, he is a liar.",
        ]

        tgt_list = ["That's stupid.",
                    "What's the problem?", "He is trustworthy."]

        print(self.score(src_list, tgt_list, batch_size))


if __name__ == "__main__":
    import pandas as pd
    from tqdm import tqdm
    import re

    bart_score = BARTScorer()

    nome_base = None

    models = [
        # "gpt-3.5-turbo",
        # "gpt-4",
        # "llama-3.1-8b-instant",
        "rag_answers",
        # "llama-3.3-70b-versatile",
        # "llama3-8b-8192",
        # "llama3-70b-8192",
    ]

    batch_size = 8  # pode ajustar conforme a GPU/CPU aguentar
    buffer_src, buffer_tgt, buffer_meta = [], [], []

    for _, row in tqdm(df.iterrows(), total=len(df)):
        # Corrige NaN
        if pd.isnull(row["Resposta_Gerada"]):
            row["Resposta_Gerada"] = ""
        if pd.isnull(row["Pergunta"]) and pd.isnull(row["Resposta"]):
            row["Pergunta"], row["Resposta"] = "", ""

        # Acumula para batch
        buffer_src.append(row["Resposta_Gerada"])
        buffer_tgt.append(row["Resposta"])
        buffer_meta.append(row)  # guarda a linha original

        # Se atingiu o tamanho do batch, processa
        if len(buffer_src) == batch_size:
            scores = bart_score.score(
                buffer_src, buffer_tgt, batch_size=batch_size)

            for r, s in zip(buffer_meta, scores):
                resultados.append(
                    {
                        "Pergunta": r["Pergunta"],
                        "Resposta_Esperada": r["Resposta"],
                        "Resposta_Gerada": r["Resposta_Gerada"],
                        "Score": s,
                    }
                )
            buffer_src, buffer_tgt, buffer_meta = [], [], []

    # Se sobrou algo menor que o batch no final, processa também
    if buffer_src:
        scores = bart_score.score(
            buffer_src, buffer_tgt, batch_size=batch_size)
        for r, s in zip(buffer_meta, scores):
            resultados.append(
                {
                    "Pergunta": r["Pergunta"],
                    "Resposta_Esperada": r["Resposta"],
                    "Resposta_Gerada": r["Resposta_Gerada"],
                    "Score": s,
                }
            )

    # Salva tudo
    pd.DataFrame(resultados).to_csv(
        f"./resultados/bartscore/{nome_base}.csv", index=False
    )
