from abc import ABC, abstractmethod
from typing import Any, Dict, Generic, List, TypeVar


T = TypeVar("T")


class BaseEvaluator(ABC, Generic[T]):
    @abstractmethod
    def score(self, *args, **kwargs) -> T:
        """
        Função para realizar a avaliação da resposta gerada em relação a resposta de referencia esperada
        """
        pass

    @abstractmethod
    def process_data_row(self, *args, **kwargs) -> List[Dict[str, Any]]:
        """
        Função para fazer o preocesameto dos dados e retorna as respostas estruturadas

        {
            "Pergunta": row["Pergunta"],
            "Resposta_Esperada": row["Resposta"],
            "Resposta_Gerada": row["Resposta_Gerada"],

            "Score": score
            ...

        }
        """
        pass

    @abstractmethod
    def test(self, *args, **kwargs) -> None:
        """
        Função para fazer teste raṕido para ver se as métricas batem com um resultado estatico
        """
        pass
