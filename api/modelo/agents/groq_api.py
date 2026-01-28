import os
from typing import Dict, List, Tuple

from dotenv import load_dotenv

from api.modelo.agents.base_aiagent import BaseAgent
from groq import Groq

load_dotenv()

GROQ_API = os.getenv("GROQ_KEY")

zero_shot: str = "Assuma o papel de um zootecnista especialista em gado leiteiro. Responda com informações diretas e aplicáveis à criação e manejo de vacas leiteiras"


MODELS_GROQ: Tuple = (
    "llama-3.3-70b-versatile",
    "llama-3.1-8b-instant",
    "llama3-70b-8192",
    "llama3-8b-8192",
    "whisper-large-v3",
    "whisper-large-v3-turbo",
)


class GroqAgent(BaseAgent):
    def __init__(
        self, model: str, zero_shot: str = zero_shot, api_key: str | None = GROQ_API
    ):
        self.model = model
        self.zero_shot = zero_shot
        self.client = Groq(api_key=api_key)

    def call(self, prompt: str):
        if prompt is None or prompt == "":
            return "Prompt vazio"

        message: List[Dict[str, str]] = [
            {"role": "system", "content": self.zero_shot},
            {"role": "user", "content": prompt},
        ]

        try:
            completions = self.client.chat.completions.create(
                model=self.model,
                message=message,
            )

            return completions.choices[0].message.content

        except Exception as e:
            print(
                f"O modelo {self.model} não foi capaz de atender a requisição. Erro: {e}"
            )
            return ""


# def groq_call(full_prompt: str, model: str, sys_prompt: str = zero_shot) -> str | None:
#     """
#     Função para fazer as consultas a API do GROQ
#
#     Args:
#         prompt: Prompt do Usuário
#         model: Nome do Modelo a ser utilizado
#         sys_prompt: Paragrafo que define o comportamento que o modelo deve tomar para gerar a resposta  (Zero | Few shots)
#
#     Returns:
#         A resposta gerada pelo modelo é retornada
#
#     Except:
#         Retornar '', caso o modelo não retorne uma resposta
#
#     """
#
#     client = Groq(api_key=GROQ_API)
#     response_full = ""
#     try:
#         completion = client.chat.completions.create(
#             model=model,
#             messages=[
#                 {"role": "system", "content": sys_prompt},
#                 {"role": "user", "content": full_prompt},
#             ],
#             stream=True,
#             temperature=1,
#             max_completion_tokens=1024,
#             top_p=1,
#             stop=None,
#         )
#
#         for chunk in completion:
#             response_full += chunk.choices[0].delta.content or ""
#
#         return response_full
#
#     except Exception:
#         return ""


if __name__ == "__main__":
    print("MODULO GROQ")
    # response = groq_call("Definição de Automação", "llama-3.3-70b")
    # print(response)

    groq_agent: GroqAgent = GroqAgent("llama3-70b", zero_shot=zero_shot)

    response: str = groq_agent.call("Definição de Automação")
    print(response)
