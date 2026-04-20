import os
from pathlib import Path
from typing import List, Literal


## GERAL
MODELS_DIR = Path(__file__).parent.parent
ZERO_SHOT_PROMPT: str = "Assuma o papel de um zootecnista especialista em gado leiteiro. Responda com informações diretas e aplicáveis à criação e manejo de vacas leiteiras"


## GPT
GPT_API_KEY = os.environ.get("CHAT_GPT_API_KEY")
LIST_OF_GPTS_MODELS: Literal["gpt-4", "gpt-5"] = "gpt-4"

## GROQ
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

LIST_OF_GROQ_MODELS: Literal[
    "llama-3.3-70b-versatile",
    "llama-3.1-8b-instant",
    "llama3-70b-8192",
    "llama3-8b-8192",
    # "whisper-large-v3",
    # "whisper-large-v3-turbo",
] = "llama-3.1-8b-instant"


##  OLLAMA
LIST_OF_OLLAMA_MODELS: Literal["gpt-oss:20b", "llama3-70b", "qwen2b"] = "gpt-oss:20b"


## Evaluators

LIST_OF_EVALUATORS: List[str] = [
    "gpt-3.5-turbo",
    "gpt-4",
    "llama-3.1-8b-instant",
    "llama-3.3-70b-versatile",
    "llama3-8b-8192",
    "llama3-70b-8192",
    "rag_answers",
    "qwen2",
    "llama3.1_rag",
]
