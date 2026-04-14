from scipy.stats import ttest_rel as t_test
import pandas as pd


# Avaliação Léxica
BLEU_DATA: pd.DataFrame = pd.read_csv("./Avaliação - BLEU.csv")
ROUGE_DATA: pd.DataFrame = pd.read_csv("./Avaliação - ROUGUE.csv")


# Avaliação  Qualidade Textual
GPTSCORE_DATA: pd.DataFrame = pd.read_csv("./Avaliação - GPTSCORE.csv")

# Avaliação Semantica
BARTSCORE_DATA: pd.DataFrame = pd.read_csv("./Avaliação - BARTSCORE.csv")
BERTSCORE_DATA: pd.DataFrame = pd.read_csv("./Avaliação - BERTSCORE.csv")


# MODELOS
LLAMA_3_8K: pd.DataFrame = pd.DataFrame()
LLAMA_3_8K["bleu"] = BLEU_DATA["llama3-8b-8192"]
LLAMA_3_8K["rouge"] = ROUGE_DATA["llama3-8b-8192"]
LLAMA_3_8K["gptscore"] = GPTSCORE_DATA["llama3-8b-8192"]
LLAMA_3_8K["bartscore"] = BARTSCORE_DATA["llama3-8b-8192"]
LLAMA_3_8K["bertscore"] = BERTSCORE_DATA["llama3-8b-8192"]

LLAMA_3_8K = LLAMA_3_8K.fillna(0)
# print(LLAMA_3_8K.tail(5))


LLAMA_3_70K: pd.DataFrame = pd.DataFrame()
LLAMA_3_70K["bleu"] = BLEU_DATA["llama3-70b-8192"]
LLAMA_3_70K["rouge"] = ROUGE_DATA["lama3-70b-8192"]
LLAMA_3_70K["gptscore"] = GPTSCORE_DATA["llama3-70b-8192"]
LLAMA_3_70K["bartscore"] = BARTSCORE_DATA["llama3-70b-8192"]
LLAMA_3_70K["bertscore"] = BERTSCORE_DATA["llama3-70b-8192"]

LLAMA_3_70K = LLAMA_3_70K.fillna(0)
# print(LLAMA_3_70K.tail(5))

GPT_4: pd.DataFrame = pd.DataFrame()
GPT_4["bleu"] = BLEU_DATA["GPT-4"]
GPT_4["rouge"] = ROUGE_DATA["gpt-4"]
GPT_4["gptscore"] = GPTSCORE_DATA["gpt4"]
GPT_4["bartscore"] = BARTSCORE_DATA["GPT-4"]
GPT_4["bertscore"] = BERTSCORE_DATA["GPT-4"]

GPT_4 = GPT_4.fillna(0)
# print(GPT_4.tail(5))


GPT_3_5: pd.DataFrame = pd.DataFrame()
GPT_3_5["bleu"] = BLEU_DATA["GPT-3.5-Turbo"]
GPT_3_5["rouge"] = ROUGE_DATA["GPT-3.5-Turbo"]
GPT_3_5["gptscore"] = GPTSCORE_DATA["gpt3.5"]
GPT_3_5["bartscore"] = BARTSCORE_DATA["GPT-3.5-Turbo"]
GPT_3_5["bertscore"] = BERTSCORE_DATA["GPT-3.5- Turbo"]

GPT_3_5 = GPT_3_5.fillna(0)
# print(GPT_3_5.tail(5))


GPT_OSS_20K: pd.DataFrame = pd.DataFrame()
GPT_OSS_20K["bleu"] = BLEU_DATA["GPT-OSS:20b"]
GPT_OSS_20K["rouge"] = ROUGE_DATA["GPT-OSS:20b"]
# GPT_OSS_20K["gptscore"] = GPTSCORE_DATA["GPT-OSS:20b"]
GPT_OSS_20K["bartscore"] = BARTSCORE_DATA["GPT-OSS:20b"]
GPT_OSS_20K["bertscore"] = BERTSCORE_DATA["GPT-OSS:20b"]

GPT_OSS_20K = GPT_OSS_20K.fillna(0)
# print(GPT_OSS_20K.tail(5))

LIGHTRAG_LLAMA_3_70K: pd.DataFrame = pd.DataFrame()
LIGHTRAG_LLAMA_3_70K["bleu"] = BLEU_DATA["LLAMA3.1 COM RAG"]
LIGHTRAG_LLAMA_3_70K["rouge"] = ROUGE_DATA["LLAMA3.1 COM RAG"]
# LIGHTRAG_LLAMA_3_70K["gptscore"] = GPTSCORE_DATA["LLAMA3.1 COM RAG"]
LIGHTRAG_LLAMA_3_70K["bartscore"] = BARTSCORE_DATA["Score"]
LIGHTRAG_LLAMA_3_70K["bertscore"] = BERTSCORE_DATA["LLAMA3.1 COM RAG"]

LIGHTRAG_LLAMA_3_70K = LIGHTRAG_LLAMA_3_70K.fillna(0)
# print(LIGHTRAG_LLAMA_3_70K.tail(5))

LIGHTRAG_GPT_OSS: pd.DataFrame = pd.DataFrame()
LIGHTRAG_GPT_OSS["bleu"] = BLEU_DATA["RAG"]
LIGHTRAG_GPT_OSS["rouge"] = ROUGE_DATA["RAG"]
# LIGHTRAG_GPT_OSS["gptscore"] = GPTSCORE_DATA["RAG"]
LIGHTRAG_GPT_OSS["bartscore"] = BARTSCORE_DATA["RAG"]
LIGHTRAG_GPT_OSS["bertscore"] = BERTSCORE_DATA["qwne2"]


LIGHTRAG_GPT_OSS = LIGHTRAG_GPT_OSS.fillna(0)
print(LIGHTRAG_GPT_OSS.tail(5))

G_LIVE_RAG_LLAMA_3: pd.DataFrame = pd.DataFrame()
G_LIVE_RAG_LLAMA_3["bleu"] = BLEU_DATA["G_RAG-LLAMA-3.1"]
G_LIVE_RAG_LLAMA_3["rouge"] = ROUGE_DATA["G-LIVE-RAG-LLAMA3.1"]
G_LIVE_RAG_LLAMA_3["gptscore"] = GPTSCORE_DATA["G_RAG + LLAMA 3.1"]
G_LIVE_RAG_LLAMA_3["bartscore"] = BARTSCORE_DATA["G-LIVE-RAG-LLAMA3.1"]
G_LIVE_RAG_LLAMA_3["bertscore"] = BERTSCORE_DATA["G-RAG + LMAMA3.1 - NAIVE"]

G_LIVE_RAG_LLAMA_3 = G_LIVE_RAG_LLAMA_3.fillna(0)
print(G_LIVE_RAG_LLAMA_3.tail(5))

G_LIVE_RAG_GPT_4: pd.DataFrame = pd.DataFrame()
G_LIVE_RAG_GPT_4["bleu"] = BLEU_DATA["G-RAG + GPT4"]
G_LIVE_RAG_GPT_4["rouge"] = ROUGE_DATA["G-RAG + GPT4"]
G_LIVE_RAG_GPT_4["gptscore"] = GPTSCORE_DATA["G RAG  + GPT 4"]
G_LIVE_RAG_GPT_4["bartscore"] = BARTSCORE_DATA["G-RAG + GPT4"]
G_LIVE_RAG_GPT_4["bertscore"] = BERTSCORE_DATA["G-RAG + GPT4"]

G_LIVE_RAG_GPT_4 = G_LIVE_RAG_GPT_4.fillna(0)
# print(G_LIVE_RAG_GPT_4.tail(5))


G_LIVE_RAG_GPT_OSS: pd.DataFrame = pd.DataFrame()
G_LIVE_RAG_GPT_OSS["bleu"] = BLEU_DATA["G-RAG + GPT-OSS:20b"]
G_LIVE_RAG_GPT_OSS["rouge"] = ROUGE_DATA["G-RAG + GPT-OSS:20b"]
# G_LIVE_RAG_GPT_OSS["gptscore"] = GPTSCORE_DATA["G-RAG + GPT-OSS:20b"]
G_LIVE_RAG_GPT_OSS["bartscore"] = BARTSCORE_DATA["G-RAG + GPT-OSS:20b"]
G_LIVE_RAG_GPT_OSS["bertscore"] = BERTSCORE_DATA["G-RAG + GPT-OSS:20b"]

G_LIVE_RAG_GPT_OSS = G_LIVE_RAG_GPT_OSS.fillna(0)
# print(G_LIVE_RAG_GPT_OSS.tail(5))
#


print("Comparação entre GPT4 vs GPT3_5")

print("BARTSCORE: ")
print(t_test(GPT_4["bartscore"], GPT_3_5["bartscore"]))
print("========" * 10, "\n")


print("BERTSCORE: ")
print(t_test(GPT_4["bertscore"], GPT_3_5["bertscore"]))
print("========" * 10, "\n")


print("GPTSCORE: ")
print(t_test(GPT_4["gptscore"], GPT_3_5["gptscore"]))
print("========" * 10, "\n")


print("BLEU: ")
print(t_test(GPT_4["bleu"], GPT_3_5["bleu"]))
print("========" * 10, "\n")


print("ROUGE: ")
print(t_test(GPT_4["rouge"], GPT_3_5["rouge"]))
print("========" * 10, "\n")
