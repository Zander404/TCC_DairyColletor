import time
import sys
import os
from transformers import GPT2Tokenizer
from openai import OpenAI  # Novo padrão
import openai  # Mantemos para capturar erros específicos


class GPT3Model(object):
    def __init__(self, model_name, api_key, logger=None):
        self.model_name = model_name
        # Inicializa o cliente moderno
        # self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.client = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")
        self.tokenizer = GPT2Tokenizer.from_pretrained("gpt2-xl")
        self.logger = logger

    def do_inference(self, input_text, output_text, max_length=2048):
        losses = []
        data = input_text + output_text

        response = self.gpt3(data)
        out = response.choices[0]  # Acesso por atributo, não dicionário

        # Na v1+, o texto retornado e os logprobs estão em objetos
        assert input_text + output_text == out.text

        # O acesso aos logprobs mudou na estrutura do objeto
        logprobs_data = out.logprobs

        # Encontrar a posição final do input
        try:
            i = logprobs_data.text_offset.index(len(input_text) - 1)
        except ValueError:
            # Caso o offset exato não seja encontrado, busca-se o mais próximo
            i = 0
            for idx, offset in enumerate(logprobs_data.text_offset):
                if offset >= len(input_text):
                    i = idx
                    break

        if i == 0:
            i = i + 1

        print("eval text", logprobs_data.tokens[i:-1])
        # Cálculo da probabilidade negativa (Loss)
        loss = -sum(logprobs_data.token_logprobs[i:-1])
        # Cálculo da Média de Perda (avg_loss)
        denominator = len(logprobs_data.text_offset) - i - 1

        if denominator <= 0:
            print(
                "⚠️ Aviso: Amostra vazia ou erro nos tokens. Atribuindo loss de penalidade."
            )
            # Atribuímos um valor alto (como 20.0) para indicar que a resposta foi péssima/inexistente
            return 20.0

        avg_loss = loss / denominator

        print("avg_loss: ", avg_loss)
        return avg_loss

    def gpt3(self, prompt, max_len=0, temp=0, num_log_probs=0, echo=True, n=None):
        response = None
        received = False
        while not received:
            try:
                # Mudança na chamada: client.completions.create
                response = self.client.completions.create(
                    model=self.model_name,
                    prompt=prompt,
                    max_tokens=max_len,
                    temperature=temp,
                    logprobs=num_log_probs,
                    echo=echo,
                    stop="\n",
                    n=n,
                )
                received = True
            except openai.BadRequestError as e:  # Antigo InvalidRequestError
                print(f"InvalidRequestError\nPrompt: {prompt}\nErro: {e}")
                raise  # Em TCC é melhor parar e ver o erro do que usar assert False
            except Exception as e:
                print("API error:", e)
                time.sleep(1)
        return response
