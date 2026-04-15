from typing import Annotated
from fastapi import APIRouter, Depends
from api.v1.extractor.services.extractor_services import ExtractorServices

router = APIRouter(prefix="/extractor_pdf")


def get_services():
    return ExtractorServices()


@router.get("")
async def start_extract_book():
    await extact_book()


SERVICES_DEP = Annotated[ExtractorServices, Depends(get_services)]


@router.get("/teste_download")
async def download_article(
    services: SERVICES_DEP, start: int = 0, limit: int = 0, max_threads: int = 2
):
    await services.download_article(start=start, limit=limit, max_threads=max_threads)
