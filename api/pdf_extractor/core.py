import os
from pathlib import Path
import fitz
import re
import asyncio
from api.utils.clean_text import clean_text
from api.utils.save_csv import save_csv

BASE_DIR = Path(__file__).resolve().parent.parent.parent

pdf_path = BASE_DIR / "500perguntasgadoleite.pdf"


async def extract_pdf():
    with open(pdf_path, "rb") as file:
        reader = fitz.open(file)
        text_total = ""

        for page in reader:
            text = page.get_text()

            text_total += text + "\n"

        text_total = re.sub(r"(\d{1,3}\n)", "", text_total)

        bloco = re.findall(
            r"(\d+\t)\s+(.*?(?:\?\s*)+)(.*?)(?=\n\d+\s+|\Z)",
            text_total,
            re.DOTALL,
        )
        result = await get_data(bloco=bloco)
        save_csv(
            "500perguntasgadoleite.csv", ["Numero", "Pergunta", "Resposta"], result
        )


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
