import os
from langchain_core import embeddings
from langchain_ollama.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.chat_models import ChatOllama
from langchain_core.runnables import RunnablePassthrough, RunnableLambda

OLLAMA_MODEL = "qwen2"
OLLAMA_EMBEDDING_MODEL = "nomic-embed-text"
CHROMA_DB_PATH = "./chroma_db_ollama/"


PROMPT_TEMPLATE = """
Você é um Especialista na área de AgroPecuária, como Veterinario Bovino e Especialista sobre produção leiteira.
Respondas as Perguntas do usuário APENAS com base no contexto fornecido abaixo.
Se a resposta não puder ser encontrada no contexto, diga educadamente que o contexto fornecido não contém a informação, mas NÃO tente inventar a resposta

CONTEXTO:
{context}

PERGUNTA DO USUÁRIO:
{question}
"""


def format_docs(docs) -> str:
    return "\n\n".join(doc.page_content for doc in docs)


def run_rag_pipeline(user_question):
    # 1º Inicializar o Banco de Dados
    embeddings = OllamaEmbeddings(model=OLLAMA_EMBEDDING_MODEL)
    vector_db = Chroma(persist_directory=CHROMA_DB_PATH,
                       embedding_function=embeddings)

    # 2º Configurar retriever
