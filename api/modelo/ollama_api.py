from dotenv import load_dotenv
from ollama import ChatResponse, chat

load_dotenv()

zero_shot: str = "Assuma o papel de um zootecnista especialista em gado leiteiro. Responda com informações diretas e aplicáveis à criação e manejo de vacas leiteiras"


async def ollama_call(
    full_prompt: str, model: str, sys_prompt: str = zero_shot
) -> str | None:
    """
    Função para fazer as consultas a API do GPT

    Args:
        prompt: Pergunta do Usuário
        model: Nome do Modelo a ser utilizado
        sys_prompt: Paragrafo que define o comportamento que o modelo deve tomar para gerar a resposta  (Zero | Few shots)

    Returns:
        A resposta gerada pelo modelo é retornada

    Except:
        Retornar '', caso o modelo não retorne uma resposta

    """

    try:
        response: ChatResponse = chat(
            model=model,
            messages=[
                {"role": "system", "content": sys_prompt},
                {"role": "user", "content": full_prompt},
            ],
        )

        return response.message.content

    except Exception:
        return ""


if __name__ == "__main__":
    print("MODULO OLLAMA (LOCAL)")
    result = ollama_call("O que significa a palavra teste?", model="qwen2")

    print(result)
