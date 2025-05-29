from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from api.pdf_extractor import core
import os

import string


router = APIRouter(prefix="/pdf_extractor")
download_path = core.pdf_downloads


@router.get("", tags=["PDF EXTRACTOR"])
async def extract_book():
    await core.extract_pdf()
    # Retorna um CSV já existente
    if not os.path.exists("500perguntasgadoleite.csv"):
        raise HTTPException(status_code=500, detail="Arquivo não foi gerado.")

    return FileResponse(
        path="500perguntasgadoleite.csv",
        media_type="text/csv",
        filename="500perguntasgadoleite.csv",
    )


@router.get("/teste_download", tags=["PDF"])
def download_article(start: int = 0, limit: int = 0, max_threads: int = 2):
    core.download_article(start=start, limit=limit, max_threads=max_threads)
