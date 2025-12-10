import os
from langchain_ollama.embeddings import OllamaEmbeddings
from langchain_ollama import ChatOllama
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableLambda

OLLAMA_MODEL = "qwen2"
OLLAMA_EMBEDDING_MODEL = "nomic-embed-text"
CHROMA_DB_PATH = "./chroma_db_ollama/"


PROMPT_TEMPLATE = """
Você é um Especialista na área de AgroPecuária, como Veterinario Bovino e Especialista sobre produção leiteira.
Responda as Perguntas do usuário APENAS com base no contexto fornecido abaixo.
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
    retriever = vector_db.as_retriever(search_kwargs={"k": 5})

    # 3º Configurar LLM
    llm = ChatOllama(model=OLLAMA_MODEL, temperature=0)
    prompt = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)

    # 4º Cadeia de RAG
    rag_chain = (
        {
            "context": retriever | RunnableLambda(format_docs),
            "question": RunnablePassthrough(),
        }
        | prompt
        | llm
    )

    # 5º Execução e Geração
    response = rag_chain.invoke(user_question)
    print("--- RESPOSTA DO LLM LOCAL ---")
    print(response.content)

    # for i, doc in enumerate(response):
    #     print(f"\n DOCUMENTO {i+1}")
    #     print(f"Conteúdo do Trecho: {doc.page_content}")
    #
    #     if doc.metadata:
    #         print(f"Fonte (Metadata): {
    #               doc.metadata.get('source', 'Não Especialista')}")
    #         print(f"Página: {doc.metadata)


if __name__ == "__main__":
    if os.path.exists(CHROMA_DB_PATH):
        pergunta = "Quem é Alexandre?"
        run_rag_pipeline(pergunta)

    else:
        print("ERRO: O Banco de Dados não foi encontrado ou carregado corretamente")
