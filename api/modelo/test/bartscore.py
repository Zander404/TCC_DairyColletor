from transformers import BartTokenizer, BartForConditionalGeneration
import torch


class BartEvaluator:
    def __init__(self, device="cpu"):
        self.tokenizer = BartTokenizer.from_pretrained("facebook/bart-large-cnn")
        self.model = BartForConditionalGeneration.from_pretrained(
            "facebook/bart-large-cnn"
        ).to(device)
        self.model.eval()

    def score(self, reference, hypothesis, normalize=True):
        input_ids = self.tokenizer(reference, return_tensors="pt").input_ids.to(
            self.model.device
        )
        with self.tokenizer.as_target_tokenizer():
            labels = self.tokenizer(hypothesis, return_tensors="pt").input_ids.to(
                self.model.device
            )

        with torch.no_grad():
            loss = self.model(input_ids=input_ids, labels=labels).loss

        if normalize:
            return -loss.item()

        else:
            return -(loss.item() * labels.size(1))


if __name__ == "__main__":
    bart_evaluator = BartEvaluator()
    reference = "Photosynthesis is the process by which plants convert sunlight into chemical energy."
    hypothesis = "Plants use sunlight to make energy, a process called photosynthesis."

    result = bart_evaluator.score(reference, hypothesis)
    print(result)

