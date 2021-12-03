from Monopoly.models.SquareModels.Square import Square
from Monopoly.models.BoardComponents import BoardComponent
from Monopoly.models.BankModel import Bank
from Monopoly.models.PlayerModel import Player

class SquareGo(Square):
    def __init__(self, board_component: BoardComponent):
        super().__init__(board_component)

    def action(self, player: Player, bank: Bank, squares, state, dice):
        bank.salary_transaction(player, 200, "Receiving 200 for passing threw Go")
