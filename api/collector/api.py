from fastapi import APIRouter
from api.collector import core

router = APIRouter(prefix="/pubmed", tags=["PubMed"])


@router.get("/")
def index():
    return {"Data": "Hello Word"}


@router.post(
    "/colect_data",
    description="Rota para realizar a busca de ID's de artigos através das Keywords pré-setadas e salvar em CSV no BackEnd",
)
def start_collect_article_id(start: int = 0, limit: int = 1000, step: int = 1000):
    core.collect_articleID(start=start, limit=limit, step=step)
    return {"Data": "Iniciando Processamento"}


@router.post(
    "/colect_abstract",
    description="Rota para fazer a coleta do resumo dos artigos coletados pela Coleta e salvar-los no CSV no BackEnd",
)
def start_collect_abstract(start: int = 0, limit: int = 0, max_threads: int = 10):
    core.collect_abstract(start=start, limit=limit, max_threads=max_threads)
    return {"Data": "Colentando Abstract dos Documentos"}
