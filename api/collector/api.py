from fastapi import APIRouter
from api.collector import core

router = APIRouter(prefix="/pubmed", tags=["PubMed"])


@router.get("/")
def index():
    return {"Data": "Hello Word"}


@router.post("/colect_data")
def start_collect_article_id(start: int = 0, limit: int = 1000, step: int = 1000):
    core.collect_articleID(start=start, limit=limit, step=step)
    return {"Data": "Iniciando Processamento"}


@router.post("/colect_abstract")
def start_collect_abastract(start: int = 0, limit: int = 0, max_threads: int = 10):
    core.collect_abstract(start=start, limit=limit, max_threads=max_threads)
    return {"Data": "Colentando Abstract dos Documentos"}
