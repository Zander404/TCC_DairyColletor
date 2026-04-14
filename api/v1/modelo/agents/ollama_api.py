from typing import Dict, List
from dotenv import load_dotenv
from ollama import ChatResponse, chat

from api.modelo.agents.base_aiagent import BaseAgent

load_dotenv()

zero_shot: str = "Assuma o papel de um zootecnista especialista em gado leiteiro. Responda com informações diretas e aplicáveis à criação e manejo de vacas leiteiras"


class OllamaAgent(BaseAgent):
    def __init__(self, model: str, zero_shot: str = zero_shot):
        self.model = model
        self.zero_shot = zero_shot

    def call(self, prompt: str) -> str | None:
        message: List[Dict[str, str]] = [
            {"role": "system", "content": self.zero_shot},
            {"role": "user", "content": prompt},
        ]

        try:
            response: ChatResponse = chat(
                model=self.model,
                messages=message,
            )

            return response.message.content

        except Exception as e:
            print(
                f"Modelo {self.model} não foi capaz de gerar uma resposta válida! Erro: {e}"
            )
            return ""


if __name__ == "__main__":
    print("MODULO OLLAMA (LOCAL)")
    agent: OllamaAgent = OllamaAgent("llama3.1-8192", zero_shot)

    result = agent.call("O que significa a palavra teste?")

    print(result)
