from Monopoly.models.MonopolyStates import RegularMonopolyState
from Monopoly.models.SquareModels.Square import Square
from Monopoly.models.BankModel import Bank
from Monopoly.models.PlayerModel import Player
from typing import List

import Monopoly.models.BoardComponents as BCs

GO_INDEX = 0
JAIL_INDEX = 30

class SquareCommunity(Square):
    def __init__(self, board_component: BCs.BoardComponent):
        super().__init__(board_component)

    def action(self, player: Player, bank: Bank, squares: List[Square], state: RegularMonopolyState, dice: int):
        card = self.draw_card(self.board_component.cardList)

        if card == 0:
            player.position = GO_INDEX
            squares[GO_INDEX].action(player, bank, squares, state, dice)

        elif card == 1:
            bank.salary_transaction(player, 200, BCs.COMMUNITY_CHEST_CARDS[card])

        elif card == 2:
            bank.charge_transaction(player, 50, None, BCs.COMMUNITY_CHEST_CARDS[card], "", state)

        elif card == 3:
            bank.salary_transaction(player, 50, BCs.COMMUNITY_CHEST_CARDS[card])

        elif card == 4:
            player.out_of_jail_card = True

        elif card == 5:
            squares[JAIL_INDEX].action(player, bank, squares, state, dice)

        elif card == 6:
            bank.salary_transaction(player, 100, BCs.COMMUNITY_CHEST_CARDS[card])

        elif card == 7:
            bank.salary_transaction(player, 20, BCs.COMMUNITY_CHEST_CARDS[card])

        elif card == 8:
            for p in state.playersInGame:
                bank.charge_transaction(p, 10, player, BCs.COMMUNITY_CHEST_CARDS[card], "Recolecting 10 from each player", state)

        elif card == 9:
            bank.salary_transaction(player, 100, BCs.COMMUNITY_CHEST_CARDS[card])

        elif card == 10:
            bank.charge_transaction(player, 100, None, BCs.COMMUNITY_CHEST_CARDS[card], "", state)

        elif card == 11:
            bank.charge_transaction(player, 50, None, BCs.COMMUNITY_CHEST_CARDS[card], "", state)

        elif card == 12:
            bank.salary_transaction(player, 25, BCs.COMMUNITY_CHEST_CARDS[card])

        elif card == 13:
            amount = self.street_repairs(player)
            bank.charge_transaction(player, amount, None, BCs.CHANCE_CARDS[card], "", state)

        elif card == 14:
            bank.salary_transaction(player, 10, BCs.COMMUNITY_CHEST_CARDS[card])

        elif card == 15:
            bank.salary_transaction(player, 100, BCs.COMMUNITY_CHEST_CARDS[card])

    def draw_card(self, card_list: List[int]):
        card = card_list.pop()
        card_list.insert(0, card)

        return card

    def street_repairs(self, player: Player):
        amount_to_pay = 0
        for prop in player.properties:
            if prop.type == "street":
                if prop.buildings < 5:
                    amount_to_pay += prop.buildings * 40
                else:
                    amount_to_pay += prop.buildings * 115

        return amount_to_pay
