from Monopoly.models.MonopolyStates import RegularMonopolyState
from Monopoly.models.SquareModels.Square import Square
from Monopoly.models.BoardComponents import BoardComponent
from Monopoly.models.BankModel import Bank
from Monopoly.models.PlayerModel import Player

class SquareStreet(Square):
    def __init__(self, street_property: BoardComponent):
        super().__init__(street_property)

    def action(self, player: Player, bank: Bank, squares, state: RegularMonopolyState, dice):
        if self.board_component.owner != None:
            rent = self.board_component.rent
            name = self.board_component.name
            bank.charge_transaction(player, self.board_component.rent, self.board_component.owner, 
                f"Paying to {self.board_component.owner.player_id} the amount {rent} after falling in {name}",
                f"Receiving {rent} from {player.player_id} for falling in {name}", state)
