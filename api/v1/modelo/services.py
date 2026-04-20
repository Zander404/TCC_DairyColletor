import asyncio
import io
from pathlib import Path
from typing import List, Literal

from tqdm import tqdm
import pandas as pd

from api.v1.modelo.agents.chatgpt_api import ChatGPTAgent
from api.v1.modelo.agents.groq_api import GroqAgent
from api.v1.modelo.agents.ollama_api import OllamaAgent
from api.v1.modelo.base.base_aiagent import BaseAgent
from api.v1.modelo.testes.evaluation_pipeline import evaluate_answers, get_evaluator
from api.v1.modelo.utils.constants import LIST_OF_EVALUATORS, MODELS_DIR

from api.v1.modelo.testes.evaluation_pipeline import BaseEvaluator

AGENTS_LIST = {"GPT": ChatGPTAgent, "GROQ": GroqAgent, "OLLAMA": OllamaAgent}


class ModeloServices:
    def __init__(self) -> None:
        pass

    async def execute_agent(
        self,
        input_content: bytes,
        result_file_name: str,
        agent: Literal["GPT", "GROQ", "OLLAMA"],
        model: str,
    ):

        agent_class = self._get_agent_class(agent)

        agent_api = agent_class(model)

        await self._generate_answers_csv(
            input_csv=input_content,
            result_file_name=result_file_name,
            api_agent=agent_api,
        )

    async def execute_evaluation(self):
        for evaluator_name in LIST_OF_EVALUATORS:
            model_evaluator: BaseEvaluator = get_evaluator(evaluator_name)
            evaluate_answers(
                model_evaluator,
                evaluator_name,
                MODELS,
            )

    def _get_agent_class(self, agent: Literal["GPT", "GROQ", "OLLAMA"]) -> BaseAgent:
        if agent not in AGENTS_LIST:
            print(f"ERRO: Agente '{agent}' não reconhecido")
            raise ValueError(
                "Opção de Agente Selcionado não existe, selecione uma opção valida",
            )

        return AGENTS_LIST[agent]

    async def _generate_answers_csv(
        self, input_csv: str, result_file_name: str, api_agent: BaseAgent
    ) -> None:
        """
        Função para fazer o processamento dos CSV base para gerar e utilizar cada modelo
        respectivo para fazer a geração da resposta com base na pergunta

        Args:
            input_csv: str   Arquivo CSV contendo as perguntas e respostas a serem geradas respostas pelo modelos
            result_file_name: str  Nome do Arquivo resultado do processamento
            api_agent: Callable Função para chamada da API de IA para gerar resposta

        """

        data: List = []

        try:
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

            pd.DataFrame(data).to_csv(f"{result_file_name}_answers.csv")

        except Exception as e:
            print("Arquivo não encontrado; Erro: ", e)


if __name__ == "__main__":
    base_file: Path = MODELS_DIR / "data" / "teste_case" / "500perguntasgadoleite.csv"
    services: ModeloServices = ModeloServices()
    decoded = base_file.read_bytes().decode("utf-8")

    reader = io.StringIO(decoded)
    asyncio.run(
        services.execute_agent(
            input_content=reader, result_file_name="model", agent="GPT", model="gpt-4"
        )
    )
