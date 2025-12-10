import os
from pathlib import Path
import fitz
import re
from api.utils.clean_text import clean_text
from api.utils.save_csv import save_csv
import asyncio

BASE_DIR = Path(__file__).resolve().parent.parent.parent
pdf_downloads = BASE_DIR / "api/downloads/"

pdf_path = BASE_DIR / "500perguntasgadoleite.pdf"
API_KEY = os.getenv("API_KEY")


async def get_data(bloco: list) -> list:
    data = []

    for numero, pergunta, resposta in bloco:
        pergunta = clean_text(pergunta)
        resposta = clean_text(resposta)
        data.append(
            {
                "Numero": numero.replace("\t", ""),
                "Pergunta": pergunta,
                "Resposta": resposta,
            }
        )

    return data


if __name__ == "__main__":
    asyncio.run(extract_pdf())
    # get_article_pdf("S0022-0302(25)00362-5")
