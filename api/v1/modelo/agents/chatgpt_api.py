from openai import OpenAI

from typing import List, Dict

from api.v1.modelo.base.base_aiagent import BaseAgent
from api.v1.modelo.utils.constants import GPT_API_KEY, ZERO_SHOT_PROMPT


class ChatGPTAgent(BaseAgent):
    def __init__(
        self, model: str, api_key: str = GPT_API_KEY, zero_shot: str = ZERO_SHOT_PROMPT
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


if __name__ == "__main__":
    print("Modulo GPT")
    model = "gpt-4"

    ## Using Strategie Pattern
    chatgpt: ChatGPTAgent = ChatGPTAgent(model=model, zero_shot=ZERO_SHOT_PROMPT)
    chatgpt.call("Definição de Automação")
