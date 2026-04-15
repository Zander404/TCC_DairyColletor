from typing import Annotated
from fastapi import APIRouter, Depends, File, UploadFile

from api.v1.extractor.services.download_services import DownloadServices


router = APIRouter(prefix="/extractor_download")


def get_services():
    return DownloadServices()


SERVICES_DEP = Annotated[DownloadServices, Depends(get_services)]


@router.post("/download")
async def download_article(
    services: SERVICES_DEP,
    input_file: UploadFile = File(...),
    start: int = 0,
    limit: int = 100,
    max_threads: int = 2,
):

    return await services.download_all(input_file=input_file, start=start, limit=limit)
