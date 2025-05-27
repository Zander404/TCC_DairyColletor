from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from api.pdf_extractor import core
import os

router = APIRouter(prefix="/pdf_extractor")


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
def download_article(pii_article):
    core.get_article_pdf(pii_article)

    if not os.path.exists("teste.pdf"):
        raise HTTPException(status_code=400, detail="ERRO")

    return FileResponse(
        path="teste.pdf", media_type="text/pdf", filename="teste_article.pdf"
    )
