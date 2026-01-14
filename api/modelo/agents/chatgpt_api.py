from openai import OpenAI
import os
from dotenv import load_dotenv

from api.modelo.agents.base_aiagent import BaseAgent
from typing import List, Dict

load_dotenv()

API_GPT: str | None = os.getenv("CHAT_GPT_KEY")

zero_shot: str = "Assuma o papel de um zootecnista especialista em gado leiteiro. Responda com informações diretas e aplicáveis à criação e manejo de vacas leiteiras"


class ChatGPTAgent(BaseAgent):
    def __init__(
        self, model: str, api_key: str = API_GPT, zero_shot: str = zero_shot
    ) -> None:
        self.model = model
        self.zero_shot = zero_shot
        self.client = OpenAI(api_key=api_key)

    def call(self, prompt: str) -> str | None:
        input: List[Dict[str, str]] = [
            {"role": "system", "content": self.zero_shot},
            {"role": "user", "content": prompt},
        ]

        try:
            response = self.client.chat.completions.create(
                model=self.model, messages=input
            )

            return response.choices[0].message.content

        except Exception:
            print(f"{self.model} não foi capaz de gerar uma resposta valida!")
            return ""


# def chatgpt_call(prompt: str, model: str, sys_prompt: str = zero_shot) -> str | None:
#     client = OpenAI(api_key=API_GPT)
#     input = [
#         {"role": "system", "content": sys_prompt},
#         {"role": "user", "content": prompt},
#     ]
#
#     try:
#         response = client.chat.completions.create(model=model, messages=input)
#         return response.choices[0].message.content
#
#     except Exception:
#         return ""


if __name__ == "__main__":
    print("Modulo GPT")
    model = "gpt-4"
    # response = chatgpt_call("Definição de Automação", model)
    # print(response)
    #
    ## Using Strategie Pattern
    chatgpt: ChatGPTAgent = ChatGPTAgent(model=model, zero_shot=zero_shot)
    chatgpt.call("Definição de Automação")
