import time
import os
from transformers import GPT2Tokenizer
from openai import OpenAI  # Novo padrão
import openai  # Mantemos para capturar erros específicos


class GPT3Model(object):
    def __init__(self, model_name, api_key, logger=None):
        self.model_name = model_name
        # Inicializa o cliente moderno
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.tokenizer = GPT2Tokenizer.from_pretrained("gpt2-xl")
        self.logger = logger

    def do_inference(self, input_text, output_text, max_length=2048):
        # GARANTIA: Se input ou output vierem como lista, detokeniza antes de somar
        if isinstance(input_text, list):
            input_text = "".join(input_text).replace(" ", " ").replace("Ġ", " ").strip()
        if isinstance(output_text, list):
            output_text = (
                "".join(output_text).replace(" ", " ").replace("Ġ", " ").strip()
            )

        data = input_text + output_text
        response = self.gpt3(data)
        out = response.choices[0]

        logprobs_data = out.logprobs

        # Encontrar a posição inicial do output no retorno da API
        i = 0
        for idx, offset in enumerate(logprobs_data.text_offset):
            if offset >= len(input_text):
                i = idx
                break

        # PRINT CORRIGIDO: Agora você verá o texto real, não a lista de tokens
        eval_tokens = logprobs_data.tokens[i:-1]
        readable_text = "".join(eval_tokens).replace(" ", " ").replace("Ġ", " ")
        print(f"--- Eval Text (Readable): {readable_text} ---")

        # Cálculo da probabilidade negativa
        loss = -sum(logprobs_data.token_logprobs[i:-1])
        denominator = len(logprobs_data.text_offset) - i - 1

        if denominator <= 0:
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
