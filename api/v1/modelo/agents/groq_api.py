from typing import Dict, List
from dotenv import load_dotenv

from groq import Groq

from api.v1.modelo.base.base_aiagent import BaseAgent
from api.v1.modelo.utils.constants import (
    GROQ_API_KEY,
    LIST_OF_GROQ_MODELS,
    ZERO_SHOT_PROMPT,
)

load_dotenv()


class GroqAgent(BaseAgent):
    def __init__(
        self,
        api_key: str | None = GROQ_API_KEY,
        model: LIST_OF_GROQ_MODELS = "llama-3.3-70b-versatile",
        zero_shot=ZERO_SHOT_PROMPT,
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
                messages=message,
            )

            return completions.choices[0].message.content

        except Exception as e:
            print(
                f"O modelo {self.model} não foi capaz de atender a requisição. Erro: {e}"
            )
            return ""


if __name__ == "__main__":
    print("MODULO GROQ")

    groq_agent: GroqAgent = GroqAgent(model="", zero_shot=ZERO_SHOT_PROMPT)

    response: str | None = groq_agent.call("Definição de Automação")
    print(response)
