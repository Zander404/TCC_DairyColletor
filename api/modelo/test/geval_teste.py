from deepeval.metrics import GEval
from deepeval.test_case.llm_test_case import LLMTestCase, LLMTestCaseParams
from deepeval import evaluate


class GEvalEvaluator:
    def __init__(self, model="gpt-4"):
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

    def score(self, test_case: list[LLMTestCase]):
        evaluate(test_cases=test_case, metrics=[self._metric])
