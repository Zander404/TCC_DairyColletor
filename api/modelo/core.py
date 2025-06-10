import os
import csv
from api.utils.save_csv import save_csv
from api.modelo.chatgpt_api import chatgpt_call
from api.modelo.groq_api import groq_call, models_groq


def generate_answers_csv(model: str, call_api):
    data: list = []
    i: int = 0

    filename = f"{model}_answers.csv"

    try:
        file_exists = os.path.exists(filename) and os.path.getsize(filename) > 0

        if not file_exists:
            filename = "500perguntasgadoleite.csv"

        print(filename)
        with open(filename, "r", newline="", encoding="utf-8") as infile:
            reader = csv.DictReader(infile)

            headers = reader.fieldnames
            if "Resposta_Gerada" not in headers:
                headers.append("Resposta_Gerada")

            for i, linha in enumerate(reader):
                if linha["Resposta_Gerada"] != "":
                    data.append(linha)
                    continue

                response = call_api(linha["Pergunta"], model)
                linha["Resposta_Gerada"] = response

                data.append(linha)

            save_csv(f"{model}_answers.csv", header=headers, data=data, save_type="w")

    except Exception as e:
        print("Arquivo não encontrado; Erro: ", e)


def main():
    # Teste com GPT
    # generate_answers_csv(model="gpt-3.5-turbo", call_api=chatgpt_call)
    ### Teste Com Groq
    for model in models_groq:
        generate_answers_csv(model, call_api=groq_call)


if __name__ == "__main__":
    main()
