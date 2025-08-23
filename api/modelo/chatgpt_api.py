from openai import OpenAI
import os
from dotenv import load_dotenv


load_dotenv()

API_GPT = os.getenv("CHAT_GPT_KEY")


def chatgpt_call(prompt: str, model):
    client = OpenAI(api_key=API_GPT)
    input = [
        {
            "role": "system",
            "content": "Assuma o papel de um zootecnista especialista em gado leiteiro. Responda com informações diretas e aplicáveis à criação e manejo de vacas leiteiras",
        },
        {"role": "user", "content": prompt},
    ]

    try:
        response = client.chat.completions.create(model=model, messages=input)
        return response.choices[0].message.content

    except:
        return ""


if __name__ == "__main__":
    print("Modulo GPT")
    model = "gpt-4"
    response = chatgpt_call("Definição de Automação", model)
    print(response)
