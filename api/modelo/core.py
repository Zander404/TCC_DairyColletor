import asyncio
import os
import pandas as pd
from tqdm import tqdm
from typing import Callable, List
from api.modelo.agents.base_aiagent import BaseAgent
from api.modelo.agents.ollama_api import OllamaAgent
from api.modelo.agents.chatgpt_api import ChatGPTAgent
from api.modelo.agents.groq_api import MODELS_GROQ, GroqAgent


async def generate_answers_csv(
    input_csv: str, model: str, api_agent: BaseAgent
) -> None:
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
                response = api_agent.call(linha["Pergunta"])
                linha["Resposta_Gerada"] = response

                data.append(linha)

        pd.DataFrame(data).to_csv(f"{model}_answers.csv")
    except Exception as e:
        print("Arquivo não encontrado; Erro: ", e)


async def main():
    teste_input_csv: str = "500perguntasgadoleite.csv"

    # # Teste com GPT
    # chatgpt_api: ChatGPTAgent = ChatGPTAgent(model="gpt-3.5-turbo")
    #
    # await generate_answers_csv(
    #     input_csv=teste_input_csv, model="gpt-3.5-turbo", api_agent=chatgpt_api
    # )

    # Teste Com Groq
    # for model in MODELS_GROQ:
    #     grop_api: GroqAgent = GroqAgent(model=model)
    #     await generate_answers_csv(
    #         input_csv=teste_input_csv, model=model, api_agent=grop_api
    #     )

    #
    # # Teste Com OLLAMA
    # ollama_api: OllamaAgent = OllamaAgent("qwen2")
    #
    # await generate_answers_csv(
    #     input_csv=teste_input_csv, model="qwen2", api_agent=ollama_api
    # )


if __name__ == "__main__":
    asyncio.run(main())
