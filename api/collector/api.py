from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from api.collector.core.collect import collect_abstract, collect_articleID
import os

router = APIRouter(prefix="/pubmed", tags=["PubMed"])


@router.get("/")
def index():
    return {"Data": "Hello Word"}


@router.get(
    "/colect_data",
    description="Rota para realizar a busca de ID's de artigos através das Keywords pré-setadas e salvar em CSV no BackEnd",
)
async def start_collect_article_id(start: int = 0, limit: int = 1000, step: int = 1000):
    await collect_articleID(
        input_file="../../../500perguntasgadoleite.csv",
        start=start,
        limit=limit,
        step=step,
    )

    return FileResponse("collect.csv", media_type="text/csv", filename="PubMedIDs.csv")


@router.get(
    "/colect_abstract",
    description="Rota para fazer a coleta do resumo dos artigos coletados pela Coleta e salvar-los no CSV no BackEnd",
)
async def start_collect_abstract(start: int = 0, limit: int = 0, max_threads: int = 10):
    await collect_abstract(
        input_file="collect.csv",
        output_file="result.csv",
        start=start,
        limit=limit,
        max_threads=max_threads,
    )
    # Retorna um CSV já existente

    if not os.path.exists("test.csv"):
        raise HTTPException(status_code=500, detail="Arquivo não foi gerado.")

    return FileResponse(path="test.csv", media_type="text/csv", filename="result.csv")
