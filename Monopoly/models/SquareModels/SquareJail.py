from Monopoly.models.SquareModels.Square import Square
from Monopoly.models.BoardComponents import BoardComponent
from Monopoly.models.PlayerModel import Player

IN_JAIL_SQUARE = 10

class SquareJail(Square):
    def __init__(self, board_component: BoardComponent):
        super().__init__(board_component)

    def action(self, player: Player, bank, squares, state, dice):
        player.position = IN_JAIL_SQUARE
        player.in_jail = True
