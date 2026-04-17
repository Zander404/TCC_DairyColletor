from typing import Annotated
from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    File,
    HTTPException,
    UploadFile,
)
from fastapi.responses import JSONResponse

from api.v1.extractor.services.download_services import DownloadServices


router = APIRouter(prefix="/extractor_download")


def get_services():
    return DownloadServices()


SERVICES_DEP = Annotated[DownloadServices, Depends(get_services)]


@router.post("/download")
async def download_article(
    background_tasks: BackgroundTasks,
    services: SERVICES_DEP,
    input_file: UploadFile = File(...),
    start: int = 0,
    limit: int = 100,
):

    try:
        await input_file.read()
    except Exception:
        raise HTTPException(status_code=400, detail=f"Falha ao ler o arquivo")

    await input_file.seek(0)
    background_tasks.add_task(
        services.download_all, input_file=input_file, start=start, limit=limit
    )

    return JSONResponse(
        status_code=202,
        content={
            "message": "Fila de Download criada",
            "description": "Confira a pasta /extractor/data/resultados",
        },
    )
