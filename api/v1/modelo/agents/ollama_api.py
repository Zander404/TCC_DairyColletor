from typing import Dict, List
from ollama import ChatResponse, chat

from api.v1.modelo.base.base_aiagent import BaseAgent
from api.v1.modelo.utils.constants import LIST_OF_OLLAMA_MODELS, ZERO_SHOT_PROMPT


class OllamaAgent(BaseAgent):
    def __init__(self, model: LIST_OF_OLLAMA_MODELS, zero_shot: str = ZERO_SHOT_PROMPT):
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
    agent: OllamaAgent = OllamaAgent(model="llama3.1-8192", zero_shot=ZERO_SHOT_PROMPT)

    result = agent.call("O que significa a palavra teste?")

    print(result)
