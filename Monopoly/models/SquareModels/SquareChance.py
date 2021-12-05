from Monopoly.models.MonopolyStates import RegularMonopolyState
from Monopoly.models.SquareModels.Square import Square
from Monopoly.models.BankModel import Bank
from Monopoly.models.PlayerModel import Player
from typing import List

import Monopoly.models.BoardComponents as BCs

BROADWALK_INDEX = 39
GO_INDEX = 0
ILLINOIS_AVENUE_INDEX = 24
ST_CHARLES_PLACE_INDEX = 11
IN_JAIL_INDEX = 10
JAIL_INDEX = 30
READING_RAILROAD = 5
RAILROAD_INDEXES = [5, 15, 25, 35]
UTILITY_INDEXES = [12, 28]

class SquareChance(Square):
    def __init__(self, board_compoenet: BCs.BoardComponent):
        super().__init__(board_compoenet)

    def action(self, player: Player, bank: Bank, squares: List[Square], state: RegularMonopolyState, dice: int):
        card = self.draw_card(self.board_component.cardList)

        if card == 0:
            player.position = BROADWALK_INDEX
            squares[BROADWALK_INDEX].action(self, player, bank, squares, state, dice)

        elif card == 1:
            player.position = GO_INDEX
            squares[GO_INDEX].action(self, player, bank, squares, state, dice)
            
        elif card == 2:
            self.must_pay_go(player, ILLINOIS_AVENUE_INDEX, bank)
            player.position = ILLINOIS_AVENUE_INDEX
            squares[ILLINOIS_AVENUE_INDEX].action(self, player, bank, squares, state, dice)

        elif card == 3:
            self.must_pay_go(player, ST_CHARLES_PLACE_INDEX, bank)
            player.position = ST_CHARLES_PLACE_INDEX
            squares[ST_CHARLES_PLACE_INDEX].action(self, player, bank, squares, state, dice)

        elif (card == 4) or (card == 5):
            railroad_index = self.get_nearest_index(RAILROAD_INDEXES, player.position)
            player.position = railroad_index
            squares[railroad_index].action(self, player, bank, squares, state, dice)

        elif card == 6:
            utility_index = self.get_nearest_index(UTILITY_INDEXES, player.position)
            player.position = utility_index
            squares[utility_index].action(self, player, bank, squares, state, dice)

        elif card == 7:
            bank.salary_transaction(player, 50, BCs.CHANCE_CARDS[card])

        elif card == 8:
            player.out_of_jail_card = True

        elif card == 9:
            player.advance_on_table(37, 40)

        elif card == 10:
            squares[JAIL_INDEX].action(self, player, bank, squares, state, dice)

        elif card == 11:
            amount = self.general_repairs(player)
            bank.charge_transaction(player, amount, None, BCs.CHANCE_CARDS[card], "", state)

        elif card == 12:
            bank.charge_transaction(player, 15, None, BCs.CHANCE_CARDS[card], "", state)

        elif card == 13:
            self.must_pay_go(player, READING_RAILROAD, bank)
            player.position = READING_RAILROAD
            squares[READING_RAILROAD].action(player, state.playersInGame, bank, squares, dice)

        elif card == 14:
            for p in state.playersInGame:
                bank.charge_transaction(player, 50, p, BCs.CHANCE_CARDS[card], "", state)

        elif card == 15:
            bank.salary_transaction(player, 150, BCs.CHANCE_CARDS[card])

    def draw_card(self, card_list: List[int]):
        card = card_list.pop()
        card_list.insert(0, card)

        return card

    def get_nearest_index(self, list_of_indexes: List[int], player_position: int):
        for i in list_of_indexes:
            if (i - player_position) > 0:
                return i

        return list_of_indexes[0]

    def must_pay_go(self, player: Player, new_position: int, bank: Bank):
        if player.position < new_position:
            bank.salary_transaction(player, 150, "Receiving 200 for passing threw Go")

    def general_repairs(self, player: Player):
        amount_to_pay = 0
        for prop in player.properties:
            if prop.type == "street":
                amount_to_pay += prop.buildings * 25

        return amount_to_pay