from Monopoly.models.SquareModels.Square import Square
from Monopoly.models.BoardComponents import BoardComponent

class SquareParking(Square):
    def __init__(self, board_component: BoardComponent):
        super().__init__(board_component)

    def action(self, player, bank, squares, state, dice):
        pass
