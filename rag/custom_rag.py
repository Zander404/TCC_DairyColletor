import os

from langchain_ollama import OllamaEmbeddings
from langchain_community.document_loaders import PyPDFLoader, DirectoryLoader
from langchain_community.vectorstores import Chroma

from langchain_text_splitters import RecursiveCharacterTextSplitter


OLLAMA_MODEL = "qwen2n"
OLLAMA_EMBEDDING_MODEL = "nomic-embed-text"

CHROMA_DB_PATH = "./chroma_db_ollama/"
PDF_DIR = "./files/"


def create_vector_database() -> None:
    print("Iniciando Banco de Dados Vetorial...")

    loader = DirectoryLoader(
        path=PDF_DIR, glob="**/*.pdf", loader_cls=PyPDFLoader, silent_errors=True
    )

    try:
        documents = loader.load()
    except Exception as e:
        print(f"Erro ao carregar o documentos: {e}")

    if not documents:
        print(f"Nenhum documento PDF foi encontrado no Diretorio {PDF_DIR}")
        return

    text_spliter = RecursiveCharacterTextSplitter(
        chunk_size=1000, chunk_overlap=200, length_function=len
    )

    chunks = text_spliter.split_documents(documents)
    print(f"Total de Documentos carregados: {len(documents)}")
    print(f"Total de Chunks: {len(chunks)}")

    # EMBEDDING dos textos

    embeddings = OllamaEmbeddings(model=OLLAMA_EMBEDDING_MODEL)

    os.makedirs(CHROMA_DB_PATH, exist_ok=True)

    vector_db = Chroma.from_documents(
        documents=chunks, embedding=embeddings, persist_directory=CHROMA_DB_PATH
    )

    vector_db.persist()

    print(f"Banco de Dados Vetorial Local criado e salvo em {CHROMA_DB_PATH}")


if __name__ == "__main__":
    create_vector_database()
