from Monopoly.models.AgentModels.BaseAgentModel import Agent
from Monopoly.models.MonopolyTableModel import MonopolyTable
from Monopoly.models.PlayerModel import Player
from Monopoly.models.BankModel import Bank
from Monopoly.models.MonopolyStates import RegularMonopolyState
from typing import List, Dict

import random
import numpy as np
import Monopoly.models.MonopolyActions as MAs

STARTING_MONEY = 1500
MAX_ACTION_MOVES = 3
GO_INDEX = 0

MAX_ITERATIONS = 10000

class MonopolyGame:
    def __init__(self, agents: List[Agent], action_log, trade_log):
        player_number = len(agents)
        self.dice = [1, 1]
        self.jail_fine = 50
        
        aux_players = [Player(player_id=i, money=STARTING_MONEY, agent=agents[i]) for i in range(0, player_number)]
        self.players = self.determine_player_order(aux_players)

        self.table = MonopolyTable()
        (properties_data, property_list, street_list, property_dic) = self.table.load_squares()

        self.bank = Bank(property_list, street_list, property_dic, properties_data, action_log, trade_log)
        self.action_log = action_log

    def determine_player_order(self, players: List[Player]) -> List[Player]:
        """
        This function is used for the initial process in which each player rolls the dice to determine the order
        of the player list.
        """
        dice_roll_list: List[int] = []
        dice_roll_dic: Dict = {}

        for i in range(len(players)):
            self.roll_dice()
            number = sum(self.dice)
            while dice_roll_list.__contains__(number):
                self.roll_dice()
                number = sum(self.dice)

            dice_roll_list.append(number)
            dice_roll_dic[number] = i

        sorted_arr = np.flip(np.sort(dice_roll_list))
        official_player_list: List[Player] = []

        for n in sorted_arr:
            idx = dice_roll_dic[n]
            official_player_list.append(players[idx])

        return official_player_list

    def roll_dice(self):
        self.dice = [random.randrange(1,6), random.randrange(1,6)]

    def move_player(self, player: Player, state: RegularMonopolyState) -> int:
        dice_val = sum(self.dice)
        if self.table.passed_threw_go(player.position, (player.position + dice_val)):
            self.table.squares[self.table.go_index].action(self, player, self.bank, self.table, state, dice_val)

        new_position = player.advance_on_table(dice_val, 40)
        return new_position

    def perform_actions(self, player: Player, player_action_list: List[MAs.ActionStructure]):
        player_actions_response = []
        performed_action_type:MAs.ActionType = []

        conclude_action: MAs.BinaryActionStructure = player_action_list.pop(0)

        for action in player_action_list:
            performed_action_type.append(action.actionType)
            res = self.action_execution(player, action)
            self.action_log.info(f"{player.agent.agent_id},{player.agent.agent_type},{action.actionType},{res[0]},{res[1]}")
            player_actions_response.append(res)
            
        return (conclude_action.response, player_actions_response, performed_action_type)

    def find_player(self, search_id: int):
        for p in self.players:
            if p.player_id == search_id:
                return p

        return None

    def action_execution(self, player: Player, action: MAs.ActionStructure):
        if action.actionType == MAs.ActionType.MakeTradeOffer:
            # Type-casting the action
            trade_offer: MAs.TradeActionStructure = action

            #Searching for the target player
            target_player = self.find_player(trade_offer.targetPlayerId)
            # If the target player was found then perform the action
            if target_player != None:
                if target_player.player_id != player.player_id:
                    return self.bank.trade_assets(trade_offer.propertyOffer, trade_offer.propertyAsked, 
                        trade_offer.moneyOffered, trade_offer.moneyAsked, player, target_player)
            
            # If the target player was not found then the initial decision was wrong
            # and the player must be informed about it.
            # An empty args list is used to indicate this error in particular
            return (False, [])

        elif action.actionType == MAs.ActionType.ImproveProperty:
            # Type-casting the action
            improve_action: MAs.PropertyActionStructure = action
            # Perform the action
            return self.bank.improve_property_transaction(improve_action.associatedPropertyList, player)

        elif action.actionType == MAs.ActionType.SellHouseOrHotel:
            unimprove_action: MAs.PropertyActionStructure = action
            return self.bank.unimprove_property_transaction(unimprove_action.associatedPropertyList, player)

        elif action.actionType == MAs.ActionType.MortgageProperty:
            mortgage_action: MAs.PropertyActionStructure = action
            return self.bank.mortgage_transaction(mortgage_action.associatedPropertyList, player)

        elif action.actionType == MAs.ActionType.FreeMortgage:
            free_mortgage_action: MAs.PropertyActionStructure = action
            return self.bank.free_mortgage_transaction(free_mortgage_action.associatedPropertyList, player)

        elif action.actionType == MAs.ActionType.UseGetOutOfJailCard:
            use_card_action: MAs.BinaryActionStructure = action
            if use_card_action.response:
                return self.bank.use_get_out_of_jail_card(player)
            else:
                return None

        elif action.actionType == MAs.ActionType.PayJailFine:
            pay_fine_action: MAs.BinaryActionStructure = action
            if pay_fine_action.response:
                return self.bank.pay_jail_fine_transaction(player, self.jail_fine)
            else: 
                return None

        elif action.actionType == MAs.ActionType.BuyProperty:
            buy_property_action: MAs.BinaryActionStructure = action
            if buy_property_action.response:
                return self.bank.buy_property_transaction(self.table.squares[player.position].board_component.property_index, 
                    player)
            else:
                self.bank.auction(self.players, self.table.squares[player.position].board_component.property_index)
                return None

    def step(self, player: Player, rest_of_players: List[Player]):
        doubles = 0 # number of doubles in the player's turn
        continue_turn = True # continue rolling the dice
        continue_actions = True
        action_count = 0
        state = RegularMonopolyState()
        state.stateType = MAs.ActionInitializationType.InitiatedByPlayer
        state.info = "From Monopoly Game"
        state.playerInTurnId = player.player_id
        state.playersInGame = self.players
        state.propertiesInGame = self.bank.properties

        while continue_turn:

            # PRE ROLL ACTIONS --------------------------------------------------------
            continue_actions = True
            action_count = 0

            # print("PRE ROLL ------------------------------------")

            while continue_actions & (action_count < MAX_ACTION_MOVES):
                if player.in_jail:
                    valid_decisions_to_take = MAs.PRE_ROLL_ACTIONS_IN_JAIL
                else:
                    valid_decisions_to_take = MAs.PRE_ROLL_ACTIONS
                
                player_action_list = player.actions(valid_decisions_to_take, state)
                (conclude, response_list, performed) = self.perform_actions(player, player_action_list)
                player.inform_decision_quality(state, performed, response_list)

                continue_actions = not conclude
                action_count += 1

            # print("OUT OF TURN ------------------------------------")
            for p in rest_of_players:
                continue_actions = True
                action_count = 0

                while continue_actions & (action_count < MAX_ACTION_MOVES):
                    player_action_list = p.actions(MAs.OUT_OF_TURN_ACTIONS, state)
                    (conclude, response_list, performed) = self.perform_actions(p, player_action_list)
                    p.inform_decision_quality(state, performed, response_list)

                    continue_actions = not conclude
                    action_count += 1

            # print("ROLLING ----------------------------------------")

            # Roll dice
            self.roll_dice()

            # If the dice is double
            if self.dice[0] == self.dice[1]:
                # print("\nDOUBLES\n")
                doubles += 1 # The number adds up

                if doubles == 3: # If the number is already 3
                    # The player goes to jail
                    self.table.squares[self.table.jail_index].action(player, self.bank, self.table.squares, state, sum(self.dice))
                    continue_turn = False # The player's turn ends
                else:
                    new_position = self.move_player(player, state)
                    self.table.squares[new_position].action(player, self.bank, self.table.squares, state, sum(self.dice))
            else:
                # If it's not a double, then the player has no right to throw again
                continue_turn = False
                new_position = self.move_player(player, state)
                self.table.squares[new_position].action(player, self.bank, self.table.squares, state, sum(self.dice))

            # POST ROLL ACTIONS -------------------------------------------------------
            # print("POST ROLL ------------------------------------")
            if (not player.in_jail) & (not player.bankrupted):
                continue_actions = True
                action_count = 0

                while continue_actions & (action_count < MAX_ACTION_MOVES):
                    if self.table.is_square_property_available(player.position):
                        valid_decisions_to_take = MAs.POST_ROLL_COUTING_PROPERTY_ACTIONS
                    else:
                        valid_decisions_to_take = MAs.POST_ROLL_ACTIONS

                    player_action_list = player.actions(valid_decisions_to_take, state)
                    (conclude, response_list, performed) = self.perform_actions(player, player_action_list)
                    player.inform_decision_quality(state, performed, response_list)

                    continue_actions = not conclude
                    action_count += 1
            else:
                continue_turn = False

    def monopoly_game(self):
        player_count = 0
        iteration_count = 0

        while (len(self.players) > 1) & (iteration_count < MAX_ITERATIONS):
            rest_of_players = [p for p in self.players if p.player_id != self.players[player_count].player_id]
            self.step(self.players[player_count], rest_of_players)

            iteration_count += 1
            player_count = (player_count + 1) % len(self.players)

        if len(self.players) > 1:
            net_values = [pl.net_value() for pl in self.players]
            idx = np.argmax(net_values)
            return self.players[idx]
        else:
            return self.players[0]