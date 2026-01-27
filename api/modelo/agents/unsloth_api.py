from typing import Dict, List
from torch.serialization import skip_data
from api.modelo.agents.base_aiagent import BaseAgent
from unsloth import FastLanguageModel
import torch


max_seq_length: int = 0
dtype = None
load_in_4bit = True


zero_shot: str = "Assuma o papel de um zootecnista especialista em gado leiteiro. Responda com informações diretas e aplicáveis à criação e manejo de vacas leiteiras"


class UnslothAgent(BaseAgent):
    def __init__(self, model: str, zero_shot: str = zero_shot):
        self.model, self.tokenizer = FastLanguageModel.from_pretrained(
            model_name=model,
            max_seq_length=2048,
        )

        FastLanguageModel.for_inference(self.model)
        self.zero_shot = zero_shot

    def call(self, prompt: str) -> str | None:
        messages: List[Dict[str, str]] = [
            {"role": "system", "content": self.zero_shot},
            {"role": "user", "content": prompt},
        ]

        try:
            inputs = self.tokenizer.apply_to_chat_template(
                messages,
                tokenizer=True,
                add_generation_prompt=True,
                return_tensors="pt",
            ).to("cuda")

            outputs = self.model.generate(
                input_ids=inputs,
                max_new_tokens=512,
                use_cache=True,
                temperature=0.5,
                top_p=0.9,
            )

            decoded_output = self.tokenizer.bath_decode(
                outputs[:, inputs.shape[1] :], skip_special_tokens=True
            )[0]

            return decoded_output.strip()

        except Exception as e:
            print(f"Erro na geração do Unsloth: {e}")
            return ""


if __name__ == "__main__":
    UnslothModel = UnslothAgent("unsloth/llama-3-8b-bnb-4bit")
