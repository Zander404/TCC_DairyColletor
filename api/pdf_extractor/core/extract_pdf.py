import re
from typing import Dict, List
import fitz

from ...utils.save_csv import save_csv
from ...utils.clean_text import clean_text


def get_data(text_block: list) -> list:
    """
    Extract and clean text_block from a pdf
    """

    def _clean_row(number: str, question: str, answer: str) -> Dict[str, str]:
        return {
            "Numero": number.replace("\t", ""),
            "Pergunta": clean_text(question),
            "Resposta": clean_text(answer),
        }

    return [
        _clean_row(number, question, answer) for number, question, answer in text_block
    ]


def extract_pdf(pdf_file: str, output_file: str) -> None:
    """
    Function to read a pdf and extract the text inside the PDF and save in a csv the important data
    Arg:
        - pdf_file: str = PDF File to analise and get the data
        - output_file: str = Name of file to save the result

    Return:
        - Return a CSV with the data extract
    """
    with open(pdf_file, "rb") as file:
        reader = fitz.open(file)

        full_text: str = "\n".join(page.get_text for page in reader)
        full_text: str = re.sub(r"(\d{1,3}\n)", "", full_text)

        BLOCK_PATTERN: str = r"(\d+\t)\s+(.*?(?:\?\s*)+)(.*?)(?=\n\d+\s+|\Z)"
        block = re.findall(BLOCK_PATTERN, full_text, re.DOTALL)

        result = get_data(block)
        save_csv(output_file, ["Numero", "Pergunta", "Resposta"], result)
