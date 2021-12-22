from abc import ABC, abstractmethod
from Monopoly.models.BoardComponents import BoardComponent


class Square(ABC):
    def __init__(self, board_component: BoardComponent):
        self.board_component = board_component

    @abstractmethod
    def action(self) -> None:
        pass