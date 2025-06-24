import math
import re
import openai


class GPTScoreEvaluator:
    def __init__(self, api_key, model="gpt-4"):
        openai.api_key = api_key
        self.model = model

    def _build_prompt(self, reference, hypothesis):
        return f"""
            Você é um avaliador automático especializado em processamento de linguagem natural.

            Sua tarefa é comparar duas respostas: uma referência (correta) e uma gerada por um modelo.

            Avalie o **nível de similaridade semântica** entre as duas respostas, isto é, se ambas transmitem as **mesmas ideias centrais**, mesmo que com palavras ou estrutura diferentes.

            Ignore variações gramaticais ou de estilo.

            ---

            **Resposta de referência:**
            {reference}

            **Resposta gerada:**
            {hypothesis}

            ---

            Com base na similaridade de conteúdo, atribua uma **nota de 1 a 5**, onde:

            - 5 = Totalmente equivalente em conteúdo
            - 4 = Quase igual, pequenas diferenças semânticas
            - 3 = Parcialmente semelhante, mas falta conteúdo importante
            - 2 = Pouca semelhança semântica
            - 1 = Sem relação semântica

            **Nota e justificativa curta:**
            """

    def score(self, reference, hypothesis):
        prompt = self._build_prompt(reference, hypothesis)

        response = openai.ChatCompletion.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0,
        )
        reply = response.choices[0].message["content"].strip()

        match = re.search(r"\b[1-5]\b", reply)
        score = int(match.group()) if match else None

        return {"score": score, "justification": reply}
