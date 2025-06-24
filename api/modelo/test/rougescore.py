from rouge_score import rouge_scorer
import rouge_score


class RougeScorerEvaluator:
    def __init__(self):
        self.scorer = rouge_scorer.RougeScorer(
            ["rouge1", "rouge2", "rougeL"], use_stemmer=True
        )

    def score(self, reference, hypothesis):
        scores = self.scorer.score(reference, hypothesis)

        return {
            "ROUGE-1": scores["rouge1"].fmeasure,
            "ROUGE-2": scores["rouge2"].fmeasure,
            "ROUGE-L": scores["rougeL"].fmeasure,
        }


if __name__ == "__main__":
    reference = "Photosynthesis is the process by which plants convert sunlight into chemical energy."
    hypothesis = "Plants use sunlight to make energy, a process called photosynthesis."

    rouge_evaluator = RougeScorerEvaluator()

    test = rouge_evaluator.score(reference, hypothesis)
    for metric, score in test.items():
        print(f"{metric}:  {score:.4f}")
