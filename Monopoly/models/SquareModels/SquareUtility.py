from Monopoly.models.SquareModels.Square import Square
from Monopoly.models.BoardComponents import BoardComponent


class SquareUtility(Square):
    def __init__(self, property: BoardComponent):
        super().__init__(property)

    def action(self):
        pass
