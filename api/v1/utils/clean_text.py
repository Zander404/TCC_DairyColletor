import re


def clean_text(text: str) -> str:
    text = re.sub(r"\b\d{3}\b\s*$", "", text.strip())
    # text = re.sub(r'\n?\b\d{1,3}\b\n?', ' ', text)

    # Corrige hífens divididos entre linhas
    text = re.sub(r"(\w+)\-\s+(\w+)", r"\1\2", text)

    # Corrige palavras quebradas por hifenização errada (ex: recomen- dação → recomendação)
    text = re.sub(r"(\w+)\xad\s*(\w+)", r"\1\2", text)

    # Remove \xa0 (espaço não separável)
    text = text.replace("\xa0", " ")

    # Remove múltiplos espaços
    text = re.sub(r"\s+", " ", text)

    return text
