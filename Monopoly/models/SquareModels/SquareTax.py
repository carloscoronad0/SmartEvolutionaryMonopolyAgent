from Monopoly.models.MonopolyStates import RegularMonopolyState
from Monopoly.models.SquareModels.Square import Square
from Monopoly.models.BoardComponents import BoardComponent
from Monopoly.models.BankModel import Bank
from Monopoly.models.PlayerModel import Player

class TaxSquare(Square):
    def __init__(self, tax: BoardComponent):
        super().__init__(tax)

    def action(self, player: Player, bank: Bank, squares, state: RegularMonopolyState, dice):
        tax = self.board_component.tax
        name = self.board_component.name
        bank.charge_transaction(player, self.board_component.rent, self.board_component.owner, 
            f"Paying to {self.board_component.owner.player_id} the amount {tax} after falling in {name}",
            f"Receiving {tax} from {player.player_id} for falling in {name}", state)
