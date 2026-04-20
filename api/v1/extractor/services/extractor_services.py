from pathlib import Path
import re
from typing import Dict
import fitz
import pandas as pd

from api.v1.extractor.utils.constants import EXTRACTOR_PATH
from api.v1.utils.clean_text import clean_text


class ExtractorServices:
    def __init__(self, results_path: str = "results") -> None:
        self.results_path = EXTRACTOR_PATH / "data" / results_path

        self.results_path.mkdir(parents=True, exist_ok=True)

    def get_data(self, text_block: list) -> list:
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
            _clean_row(number, question, answer)
            for number, question, answer in text_block
        ]

    def extract_pdf(
        self, pdf_file: str = "500perguntasgadoleite.pdf"
    ) -> pd.DataFrame | None:
        """
        Function to read a pdf and extract the text inside the PDF and save in a csv the important data
        Arg:
            - pdf_file: str = PDF File to analise and get the data
            - output_file: str = Name of file to save the result

        Return:
            - Return a CSV with the data extract
        """
        pdf_filepath: Path = EXTRACTOR_PATH / "data" / pdf_file
        with open(str(pdf_filepath), "rb") as file:
            reader = fitz.open(file)

            full_text: str = "\n".join(page.get_text() for page in reader)
            full_text: str = re.sub(r"(\d{1,3}\n)", "", full_text)

            BLOCK_PATTERN: str = r"(\d+\t)\s+(.*?(?:\?\s*)+)(.*?)(?=\n\d+\s+|\Z)"
            block = re.findall(BLOCK_PATTERN, full_text, re.DOTALL)

            result = self.get_data(block)

            df_data = pd.DataFrame(result, columns=["Numero", "Pergunta", "Resposta"])

            return df_data
