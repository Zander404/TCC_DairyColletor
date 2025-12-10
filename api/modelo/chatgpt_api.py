from openai import OpenAI
import os
from dotenv import load_dotenv


load_dotenv()

API_GPT = os.getenv("CHAT_GPT_KEY")

zero_shot: str = "Assuma o papel de um zootecnista especialista em gado leiteiro. Responda com informações diretas e aplicáveis à criação e manejo de vacas leiteiras"


def chatgpt_call(prompt: str, model: str, sys_prompt: str = zero_shot) -> str | None:
    """
    Função para fazer as consultas a API do GPT

    Args:
        prompt: Prompt do Usuário
        model: Nome do Modelo a ser utilizado
        sys_prompt: Paragrafo que define o comportamento que o modelo deve tomar para gerar a resposta  (Zero | Few shots)

    Returns:
        A resposta gerada pelo modelo é retornada

    Except:
        Retornar '', caso o modelo não retorne uma resposta

    """

    client = OpenAI(api_key=API_GPT)
    input = [
        {"role": "system", "content": sys_prompt},
        {"role": "user", "content": prompt},
    ]

    try:
        response = client.chat.completions.create(model=model, messages=input)
        return response.choices[0].message.content

    except Exception:
        return ""


if __name__ == "__main__":
    print("Modulo GPT")
    model = "gpt-4"
    response = chatgpt_call("Definição de Automação", model)
    print(response)
