from typing import List
from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API = os.getenv("GROQ_KEY")

zero_shot: str = "Assuma o papel de um zootecnista especialista em gado leiteiro. Responda com informações diretas e aplicáveis à criação e manejo de vacas leiteiras"


models_groq: List = [
    "llama-3.3-70b-versatile",
    "llama-3.1-8b-instant",
    "llama3-70b-8192",
    "llama3-8b-8192",
    "whisper-large-v3",
    "whisper-large-v3-turbo",
]


def groq_call(full_prompt: str, model: str, sys_prompt: str = zero_shot) -> str | None:
    """
    Função para fazer as consultas a API do GROQ

    Args:
        prompt: Prompt do Usuário
        model: Nome do Modelo a ser utilizado
        sys_prompt: Paragrafo que define o comportamento que o modelo deve tomar para gerar a resposta  (Zero | Few shots)

    Returns:
        A resposta gerada pelo modelo é retornada

    Except:
        Retornar '', caso o modelo não retorne uma resposta

    """

    client = Groq(api_key=GROQ_API)
    response_full = ""
    try:
        completion = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": sys_prompt},
                {"role": "user", "content": full_prompt},
            ],
            stream=True,
            temperature=1,
            max_completion_tokens=1024,
            top_p=1,
            stop=None,
        )

        for chunk in completion:
            response_full += chunk.choices[0].delta.content or ""

        return response_full

    except Exception:
        return ""


if __name__ == "__main__":
    print("MODULO GROQ")
    response = groq_call("Definição de Automação", "llama-3.3-70b")
    print(response)
