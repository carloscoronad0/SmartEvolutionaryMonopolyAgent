from Monopoly.models.SquareModels.Square import Square
from Monopoly.models.BoardComponents import BoardComponent


class SquareChance(Square):
    def __init__(self, board_compoenet: BoardComponent):
        super().__init__(board_compoenet)

    def action(self):
        pass
