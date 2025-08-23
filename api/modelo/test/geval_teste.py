from deepeval.metrics import GEval
from deepeval.test_case.llm_test_case import LLMTestCase, LLMTestCaseParams
from deepeval import evaluate, test_case
from numpy import result_type
import re


class GEvalEvaluator:
    def __init__(self, model="gpt-4o"):
        self.model = model

        self._metric = GEval(
            threshold=0.75,
            name="SimilariaridadeTextual",
            evaluation_steps=[
                "Avalie se o conteúdo essencial é preservado entre textos",
                "Ignores variações lexicas ou estilo",
                "Penalize omissão de informações importantes",
            ],
            evaluation_params=[
                LLMTestCaseParams.ACTUAL_OUTPUT,
                LLMTestCaseParams.EXPECTED_OUTPUT,
            ],
            model=self.model,
        )

    def evaluate(self, test_case: LLMTestCase):
        evaluate(test_cases=[test_case], metrics=[self._metric])


def test():
    geval_evaluator = GEvalEvaluator()

    test_case = [
        LLMTestCase(
            input="O que é fotossíntese?",
            actual_output="Plantas fazem açúcar usando luz do sol.",
            expected_output="Fotossíntese é o processo pelo qual as plantas convertem luz solar em energia química.",
        ),
    ]

    geval_evaluator.score(test_case)



if __name__ == "__main__":
    import pandas as pd
    from tqdm import tqdm

    resultados = []
    geval_evaluator = GEvalEvaluator()
    models = [
        "gpt-3.5-turbo",
        "llama-3.1-8b-instant",
        "llama-3.3-70b-versatile",
        "llama3-8b-8192",
        "llama3-70b-8192",
    ]

    for model in models:
        path = f"./data/{model}_answers.csv"
        df = pd.read_csv(path)

        df["Resposta"] = df["Resposta"].fillna("resposta ausente")

        match = re.search(r"\./data/([a-zA-Z0-9\-_.]+)\.csv", path)
        nome_base = None
        if match:
            nome_base = match.group(1)
            print(nome_base)

        if nome_base:
            for _, row in tqdm(df.iterrows(), total=len(df)):
                if (
                    pd.isnull(row["Pergunta"])
                    or pd.isnull(row["Resposta"])
                    or pd.isnull(row["Resposta_Gerada"])
                ):
                    continue

                test_case = LLMTestCase(
                    input=str(row["Pergunta"]),
                    expected_output=str(row["Resposta"]),
                    actual_output=str(row["Resposta_Gerada"]),
                )
                evaluation_case = geval_evaluator.evaluate(test_case)
                metric_name = geval_evaluator._metric.name
                if evaluation_case is None:
                    continue

                resultados.append(
                    {
                        "Pergunta": row["Pergunta"],
                        "Resposta_Esperada": row["Resposta"],
                        "Resposta_Gerada": row["Resposta_Gerada"],
                        "Score": evaluation_case.outputs[metric_name].score,
                        "Passou": evaluation_case.outputs[metric_name].is_successful(),
                        "Justificativa": evaluation_case.outputs[metric_name].reason,
                    }
                )
            pd.DataFrame(resultados).to_csv(f"./resultados/geval/{nome_base}.csv")
