from fastapi import APIRouter, UploadFile, File
from api.v1.collector.services import (
    start_collect_abstract,
    start_collect_article_id_pub_med,
)

router = APIRouter(prefix="/pubmed", tags=["PubMed"])


@router.get("/")
def index():
    return {"Data": "Hello Word"}


@router.post(
    "/colect_data",
    description="Rota para realizar a busca de ID's de artigos através das Keywords pré-setadas e salvar em CSV no BackEnd",
)
async def collect_article_id(
    start: int = 0,
    limit: int = 1000,
    step: int = 1000,
):

    return await start_collect_article_id_pub_med(start, limit, step)


@router.post(
    "/colect_abstract",
    description="Rota para fazer a coleta do resumo dos artigos coletados pela Coleta e salvar-los no CSV no BackEnd",
)
async def collect_abstract(
    file: UploadFile = File(...),
    start: int = 0,
    limit: int = 1000,
    max_threads: int = 10,
):
    return await start_collect_abstract(
        start=start, limit=limit, max_threads=max_threads, file_with_ids=file
    )
