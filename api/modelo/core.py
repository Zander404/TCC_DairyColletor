import asyncio
import os
import csv
import pandas as pd
from tqdm import tqdm
from typing import Callable, List
from api.modelo import ollama_api
from api.utils.save_csv import save_csv
from api.modelo.chatgpt_api import chatgpt_call
from api.modelo.groq_api import groq_call, models_groq


async def generate_answers_csv(input_csv: str, model: str, call_api: Callable) -> None:
    """
    Função para fazer o processamento dos CSV base para gerar e utilizar cada modelo
    respectivo para fazer a geração da resposta com base na pergunta

    Args:
        input_csv: str   Arquivo CSV contendo as perguntas e respostas a serem geradas respostas pelo modelos
        model: str  Nome do Modelo a ser usado
        call_api: Callable Função para chamada da API de IA para gerar resposta

    Return:
        Retorna NULL, mas gera um pdf na pasta principal do projeto com o nome no padrão
        f{model}_answers.csv
    """

    data: List = []

    try:
        if os.path.exists(input_csv) and os.path.getsize(input_csv) < 0:
            raise Exception("O Arquivo não existe")

        df = pd.read_csv(input_csv)

        if "Resposta_Gerada" not in df.columns:
            df["Resposta_Gerada"] = None

        for _, linha in tqdm(df.iterrows(), total=len(df)):
            if pd.notnull(linha["Resposta_Gerada"]):
                data.append(linha)
                continue

            else:
                response = await call_api(linha["Pergunta"], model)
                linha["Resposta_Gerada"] = response

                data.append(linha)

        pd.DataFrame(data).to_csv(f"{model}_answers.csv")
        # withopen(input_csv, "r", newline="", encoding="utf-8") as infile:
        #     reader = csv.DictReader(infile)
        #     headers = reader.fieldnames
        #     if "Resposta_Gerada" not in headers:
        #         headers.append("Resposta_Gerada")
        #
        #     for _, linha in tqdm(reader, total=le):
        #         if linha["Resposta_Gerada"] != "":
        #             data.append(linha)
        #             continue
        #
        #         else:
        #             response = await call_api(linha["Pergunta"], model)
        #             linha["Resposta_Gerada"] = response
        #
        #             data.append(linha)
        #     pd.Dataframe(data).to_csv(f"{model}_answers.csv")

    except Exception as e:
        print("Arquivo não encontrado; Erro: ", e)


async def main():
    # teste_input_csv: str = "500perguntasgadoleite.csv"

    teste_input_csv: str = "qwen2_answers.csv"
    # # Teste com GPT
    # await generate_answers_csv(input_csv=teste_input_csv, model="gpt-3.5-turbo", call_api=chatgpt_call)
    #
    # # Teste Com Groq
    # for model in models_groq:
    #     await generate_answers_csv(
    #         input_csv=teste_input_csv, model=model, call_api=groq_call
    #     )
    #
    #
    await generate_answers_csv(
        input_csv=teste_input_csv, model="qwen2", call_api=ollama_api.ollama_call
    )


if __name__ == "__main__":
    asyncio.run(main())
