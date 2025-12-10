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
            "500perguntasgadoleite.csv", [
                "Numero", "Pergunta", "Resposta"], result
        )
