from typing import Any, Dict, List, Tuple
from torch.serialization import skip_data
from api.modelo.agents.base_aiagent import BaseAgent
from unsloth import FastLanguageModel
import torch

zero_shot: str = "Assuma o papel de um zootecnista especialista em gado leiteiro. Responda com informações diretas e aplicáveis à criação e manejo de vacas leiteiras"


class UnslothAgent(BaseAgent):
    def __init__(self, model_id: str, zero_shot: str = zero_shot):
        # 1. Carregamento otimizado (4-bit é o ideal para Unsloth)
        self.model, self.tokenizer = FastLanguageModel.from_pretrained(
            model_name=model_id,
            max_seq_length=2048,
            load_in_4bit=True,
        )

        # 2. Ativação de kernels de inferência (essencial para velocidade)
        FastLanguageModel.for_inference(self.model)

        self.model_id = model_id
        self.zero_shot = zero_shot

    def call(self, prompt: str) -> str:
        """Segue a interface simplificada de agente."""
        messages = [
            {"role": "system", "content": self.zero_shot},
            {"role": "user", "content": prompt},
        ]

        # Chamamos o método interno que lida com o motor Unsloth
        content, _ = self.complete_chat(messages)
        return content

    def complete_chat(self, messages: List[Dict[str, str]]) -> Tuple[str, Any]:
        """Implementação que segue o contrato do GeneralOpenAIClient."""
        try:
            # apply_chat_template (e não apply_to_chat_template)
            # tokenize=True (e não tokenizer=True)
            inputs = self.tokenizer.apply_chat_template(
                messages,
                tokenize=True,
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

            # batch_decode (e não bath_decode)
            decoded_output = self.tokenizer.batch_decode(
                outputs[:, inputs.shape[1] :], skip_special_tokens=True
            )[0]

            # Mock do objeto de resposta para compatibilidade
            raw_response = self._create_mock_response(decoded_output.strip())

            return decoded_output.strip(), raw_response

        except Exception as e:
            print(f"Erro na geração do Unsloth: {e}")
            return "", None

    def _create_mock_response(self, content: str) -> Any:
        """Simula a estrutura de retorno da OpenAI/Ollama."""

        class MockObj:
            def __init__(self, **kwargs):
                self.__dict__.update(kwargs)

        return MockObj(choices=[MockObj(message=MockObj(content=content))])


if __name__ == "__main__":
    # Teste rápido
    agent = UnslothAgent("unsloth/llama-3-8b-bnb-4bit")
    resposta = agent.call("Qual a melhor dieta para vacas no pré-parto?")
    print(f"\nZootecnista AI: {resposta}")
