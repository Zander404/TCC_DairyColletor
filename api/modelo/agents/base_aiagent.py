from abc import abstractmethod, ABC


class BaseAgent(ABC):
    def __init__(self, model: str, api_key: str | None, zero_shot: str) -> None:
        self.model = model
        self.zero_shot = zero_shot
        self.api_key = api_key

    def setModel(self, model: str) -> None:
        """
        Fazer a troca do modelo sem ter que recriar a Classe
        """

        self.model = model

    @abstractmethod
    def call(self, prompt: str) -> str | None:
        """
        Função para fazer as consultas aos Modelos de IA

        Args:
            prompt: Prompt do Usuário
            model: Nome do Modelo a ser utilizado
            sys_prompt: Paragrafo que define o comportamento que o modelo deve tomar para gerar a resposta  (Zero | Few shots)

        Returns:
            A resposta gerada pelo modelo é retornada

        Except:
            Retornar '', caso o modelo não retorne uma resposta

        """

        pass
