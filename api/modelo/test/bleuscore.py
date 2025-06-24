import nltk
from nltk.translate.bleu_score import corpus_bleu, sentence_bleu
from pydantic_core.core_schema import list_schema

nltk.download("punkt_tab")


class BleuScore:
    def __init__(self, weights: tuple[float, float, float, float]):
        self.weights = weights

    def score(self, reference_text: str, prediction_text: str):
        reference = [nltk.word_tokenize(reference_text)]
        prediction = nltk.word_tokenize(prediction_text)
        return sentence_bleu(reference, prediction, weights=self.weights)

    def test(self):
        reference = "the picture is clicked by me"

        predictions = "the picture the picture by me"

        result = self.score(reference, predictions)
        assert result == 0.7186082239261684


if __name__ == "__main__":
    blue_score = BleuScore(weights=(0.25, 0.25, 0, 0))
    result = blue_score.test()
