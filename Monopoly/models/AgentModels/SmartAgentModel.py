from Monopoly.models.AgentModels.BaseAgentModel import Agent
from typing import List
from Network.DDQNActor import DdqnActor

import numpy as np
import Monopoly.models.BoardComponents as BCs
import Monopoly.models.MonopolyActions as MAs
import Monopoly.models.MonopolyStates as MSs
import math

MONOPOLY_TABLE_SIZE = 40
INITIAL_NUMBER_OF_PLAYERS = 4

REGULAR_INPUT_NUM = 272
REGULAR_OUTPUT_NUM = 165

TRADING_INPUT_NUM = 114
TRADING_OUTPUT_NUM = 3

STARTING_HIDDEN_SIZE = [64, 64]
STARTING_HIDDEN_ACTIVATION = ['relu', 'relu']

TRADING_ACTIONS = [MAs.ActionType.ContinueInAuction, MAs.ActionType.AcceptTradeOffer]

STREETS_COLORS = ["purple", "lightblue", "violet", "orange", "red", "yellow", "darkgreen", "darkblue"]

class SmartAgent(Agent):
    def __init__(self, agent_id: int, regular_memory_replay, trading_memory_replay):
        super().__init__(agent_id, "smart")

        self.regular_replay_memory = regular_memory_replay
        self.trading_replay_memory = trading_memory_replay

        self.regular_actor = DdqnActor(REGULAR_INPUT_NUM, REGULAR_OUTPUT_NUM, 0.003, 0.80, 0.02, 0.5, regular_memory_replay, "regular")
        self.trading_actor = DdqnActor(TRADING_INPUT_NUM, TRADING_OUTPUT_NUM, 0.003, 0.80, 0.02, 0.5, trading_memory_replay, "trading")

        self.order_dic = None
        self.last_state = None
        self.last_decision = None

    def take_decisions(self, valid_decisions_to_take: List[MAs.ActionType], state: MSs.MonopolyState) -> List[MAs.ActionStructure]:

        if state.stateType == MAs.ActionInitializationType.InitiatedByOtherEntity:
            return self.take_trading_decisions(state, valid_decisions_to_take)
        elif state.stateType == MAs.ActionInitializationType.InitiatedByPlayer:
            return self.take_regular_decisions(state, valid_decisions_to_take)

    def decision_quality(self, resulting_state: MSs.MonopolyState, decisions_to_inform: List[MAs.ActionType], 
        args_list):

        if resulting_state.stateType == MAs.ActionInitializationType.InitiatedByOtherEntity:
            next_state = self.form_trading_state(resulting_state)
            (p_prop_num, mn_op_prop, num_clr_compl, h_build, pl_mny, mn_op_mny) = self.get_reward_parameters_from_trade(resulting_state)
            reward = self.reward_function(p_prop_num, mn_op_prop, num_clr_compl, h_build, pl_mny, mn_op_mny)
            self.trading_replay_memory.push(self.last_state, self.last_decision, reward, next_state)

        elif resulting_state.stateType == MAs.ActionInitializationType.InitiatedByPlayer:
            next_state = self.form_regular_state(resulting_state)
            (p_prop_num, mn_op_prop, num_clr_compl, h_build, pl_mny, mn_op_mny) = self.get_reward_parameters_from_regular(resulting_state)
            reward = self.reward_function(p_prop_num, mn_op_prop, num_clr_compl, h_build, pl_mny, mn_op_mny)
            self.regular_replay_memory.push(self.last_state, self.last_decision, reward, next_state)

        self.rewards_in_game += reward
        self.order_dic = None
        self.last_state = None
        self.last_decision = None

    def clone(self, ag_id):
        clone = type(self)(agent_id = ag_id,
                            regular_memory_replay = self.regular_replay_memory,
                            trading_memory_replay = self.trading_replay_memory)

        clone.agent_id = ag_id
        clone.agent_type = "smart"
        clone.id_in_game = -1
        clone.rewards_in_game = 0
        clone.reward_count = 0
        clone.regular_actor = self.regular_actor.clone()
        clone.trading_actor = self.trading_actor.clone()

        return clone
        
    #region ACTIONS_INITIATED_BY_PLAYER

    def make_trade_offer(self, trade_binary_representation: np.ndarray) -> MAs.TradeActionStructure:
        """
        Punish if: 
            - Property is not Owned by the player
            - Property has houses or a hotel

        Format:
            - [Offered Properties] -> 28
            - [Wished Properties] -> 28
            - [Money offered] -> 1 : Percentage * own Money
            - [Wished Money] -> 1 : Percentage * oponents Money
            - [Target Player] -> 3 : [PA, PB, PC]
        """

        property_offering = np.round(trade_binary_representation[0:28])
        property_asked = np.round(trade_binary_representation[28:56])
        percentage_money_offered = trade_binary_representation[56]
        percentage_money_asked = trade_binary_representation[57]
        player = np.round(trade_binary_representation[58:61])

        offer = np.where(property_offering == 1)[0]
        asked = np.where(property_asked == 1)[0]

        if percentage_money_offered > 0:
            money_offer = self._transform_money(100, percentage_money_offered)
        else:
            money_offer = 0

        if percentage_money_asked > 0:
            money_ask = self._transform_money(100, percentage_money_asked)
        else: 
            money_ask = 0

        player_selection = np.where(player == 1)[0]
        if len(player_selection) > 1:
            # The plus 1 is because in order_dic the index 0 is ocupied by the player id who works with this agent
            if (player_selection[0] + 1) < len(self.order_dic):
                target_player_id = self.order_dic[(player_selection[0] + 1)]
            else:
                target_player_id = -1
        else:
            target_player_id = -1

        trade_offer = MAs.TradeActionStructure(MAs.ActionType.MakeTradeOffer, offer.tolist(), asked.tolist(), 
            money_offer, money_ask, target_player_id)

        # print(f"Taking trade decision from agent {self.agent_id}")
        # print(trade_offer)

        return trade_offer

    def improve_property(self, streets_binary: np.ndarray) -> MAs.PropertyActionStructure:
        indicated_streets = np.round(streets_binary)
        indicated_idxs = np.where(indicated_streets == 1)[0]
        improve_decision = MAs.PropertyActionStructure(MAs.ActionType.ImproveProperty, indicated_idxs.tolist(), MAs.PropertyType.Street)
        # print(f"Taking improve decision from agent {self.agent_id}")
        # print(improve_decision)
        return improve_decision

    def sell_house_hotel(self, streets_binary: np.ndarray) -> MAs.PropertyActionStructure:
        indicated_streets = np.round(streets_binary)
        indicated_idxs = np.where(indicated_streets == 1)[0]
        sell_decision = MAs.PropertyActionStructure(MAs.ActionType.SellHouseOrHotel, indicated_idxs.tolist(), 
            MAs.PropertyType.Street)
        # print(f"Taking sell house decision from agent {self.agent_id}")
        # print(sell_decision)
        return sell_decision
    
    def mortgage_properties(self, mortgage_binary: np.ndarray) -> MAs.PropertyActionStructure:
        indicated_mortgage = np.round(mortgage_binary)
        indicated_idxs = np.where(indicated_mortgage == 1)[0]
        mortgage_decision = MAs.PropertyActionStructure(MAs.ActionType.MortgageProperty, indicated_idxs.tolist(), 
            MAs.PropertyType.Property)
        # print(f"Taking mortgage decision from agent {self.agent_id}")
        # print(mortgage_decision)
        return mortgage_decision

    def free_mortgage(self, free_binary: np.ndarray) -> MAs.PropertyActionStructure:
        indicated_free = np.round(free_binary)
        indicated_idxs = np.where(indicated_free == 1)[0]
        free_decision = MAs.PropertyActionStructure(MAs.ActionType.FreeMortgage, indicated_idxs.tolist(), 
            MAs.PropertyType.Property)
        # print(f"Taking free decision from agent {self.agent_id}")
        # print(free_decision)
        return free_decision

    def conclude_actions(self, conclude_binary) -> MAs.BinaryActionStructure:
        conclude = np.round(conclude_binary) == 1
        conclude_decision = MAs.BinaryActionStructure(MAs.ActionType.ConcludeActions, conclude)
        # print(f"Taking conclude decision from agent {self.agent_id}")
        # print(conclude_decision)
        return conclude_decision

    def use_get_out_of_jail_card(self, use_card_binary) -> MAs.BinaryActionStructure:
        use_card = np.round(use_card_binary) == 1
        use_card_decision = MAs.BinaryActionStructure(MAs.ActionType.UseGetOutOfJailCard, use_card)
        # print(f"Taking use card decision from agent {self.agent_id}")
        # print(use_card_decision)
        return use_card_decision

    def pay_jail_fine(self, pay_fine_binary) -> MAs.BinaryActionStructure:
        pay_fine = np.round(pay_fine_binary) == 1
        pay_decision = MAs.BinaryActionStructure(MAs.ActionType.PayJailFine, pay_fine)
        # print(f"Taking pay jail fine decision from agent {self.agent_id}")
        # print(pay_decision)
        return pay_decision

    def buy_property(self, buy_binary) -> MAs.BinaryActionStructure:
        buy = np.round(buy_binary) == 1
        buy_decision = MAs.BinaryActionStructure(MAs.ActionType.BuyProperty, buy)
        # print(f"Taking buy decision from agent {self.agent_id}")
        # print(buy_decision)
        # input()
        return buy_decision

    #endregion ACTIONS_INITIATED_BY_PLAYER

    #region ACTIONS_INITIATED_BY_OTHER_ENTITY

    def accept_trade_offer(self, accept_binary) -> MAs.BinaryActionStructure:
        accept = np.round(accept_binary) == 1
        accept_decision = MAs.BinaryActionStructure(MAs.ActionType.AcceptTradeOffer, accept)
        # print(f"Taking accept trade decision from agent {self.agent_id}")
        # print(accept_decision)
        return accept_decision

    def continue_in_auction(self, continue_binary) -> MAs.AuctionActionStructure:
        cont = np.round(continue_binary[0])
        money_to_bid = self._transform_money(100, continue_binary[1])
        continue_decision = MAs.AuctionActionStructure(MAs.ActionType.ContinueInAuction, cont, money_to_bid)
        # print(f"Taking continue in auction decision from agent {self.agent_id}")
        # print(continue_decision)
        return continue_decision

    #endregion ACTIONS_INITIATED_BY_OTHER_ENTITY

    #region AUX_FUNCTIONS

    @staticmethod
    def _transform_money(baseline_money: float, percentage: float) -> int:
        return int(percentage * baseline_money)

    # To return the regular state adapted to a numeric form (state space) for the neural network
    def form_regular_state(self, state: MSs.RegularMonopolyState) -> np.ndarray:
        total_info = []
        # PLAYER STATE SECTION -----------------------------------------------
        all_money = [pl.money for pl in state.playersInGame]
        mean_money = sum(all_money) / len(all_money)

        total_info = []
        player_order = []
        for pl in state.playersInGame:
            temp_position = pl.position / MONOPOLY_TABLE_SIZE
            temp_money = pl.money / mean_money
            temp_sets = pl.sets_completed / len(STREETS_COLORS)

            if pl.player_id == self.id_in_game:
                player_order.insert(0, pl.player_id)

                total_info.insert(0, temp_sets)
                total_info.insert(0, int(pl.out_of_jail_card))
                total_info.insert(0, int(pl.in_jail))
                total_info.insert(0, temp_money)
                total_info.insert(0, temp_position)
            else:
                player_order.append(pl.player_id)

                total_info.append(temp_position)
                total_info.append(temp_money)
                total_info.append(int(pl.in_jail))
                total_info.append(int(pl.out_of_jail_card))
                total_info.append(temp_sets)

        # Initial number of players minus the actual number
        # Used for padding the total_info list to mantain the same state size
        difference = INITIAL_NUMBER_OF_PLAYERS - len(state.playersInGame)
        if difference > 0:
            for _ in range(difference):
                # Padding
                total_info.extend([0 for _ in range(5)])

        # --------------------------------------------------------------------

        # PROPERTY STATE SECTION ---------------------------------------------
        all_rent = [prop.rent for prop in state.propertiesInGame]
        mean_rent = sum(all_rent) / len(all_rent)

        for prop in state.propertiesInGame:
            temp_owner = [0 for _ in range(INITIAL_NUMBER_OF_PLAYERS)]
            if prop.owner != None:
                temp_owner[player_order.index(prop.owner.player_id)] = 1

            total_info.extend(temp_owner)
            total_info.append(int(prop.mortgage))

            temp_rent = prop.rent / mean_rent
            total_info.append(temp_rent)

            if prop.type == "street":
                total_info.append(int(prop.set_completed))
                temp_buildings = prop.buildings / BCs.MAX_IMPROVEMENTS
                total_info.append(temp_buildings)
                pos_color = STREETS_COLORS.index(prop.street_color)
                temp_color = pos_color / len(STREETS_COLORS)
                total_info.append(temp_color)
            else:
                total_info.extend([0 for _ in range(3)])
        # --------------------------------------------------------------------
        total_info_np = np.array(total_info)

        self.last_state = np.array(total_info)
        self.order_dic = player_order

        return total_info_np

    # To return the offer (trade) state adapted to a numeric form (state space) for the neural network
    def form_trading_state(self, state: MSs.OfferActionMonopolyState) -> np.ndarray:
        # Property Trade Info ------------------------------------------------
        offer_prop_info = self.get_binary_representation(state.offerdProperties, 28)
        asked_prop_info = self.get_binary_representation(state.askedProperties, 28)
        # --------------------------------------------------------------------

        # Money Trade Info ---------------------------------------------------
        if state.targetPlayer.money > 0:
            metric = state.targetPlayer.money
        else:
            metric = 1

        adapted_money_offer = state.moneyOffer / metric
        adapted_money_asked = state.moneyAsked / metric
        # --------------------------------------------------------------------

        # Players Properties Info --------------------------------------------
        if state.initialPlayer != None:
            initial_repr = self.get_binary_representation(state.initialPlayer.properties, 28)
        else:
            # To get just 0s for padding
            initial_repr = self.get_binary_representation([], 28)

        if state.targetPlayer != None:
            target_repr = self.get_binary_representation(state.targetPlayer.properties, 28)
        else:
            # To get just 0s for padding
            target_repr = self.get_binary_representation([], 28)

        # --------------------------------------------------------------------

        total_info = []
        total_info.extend(offer_prop_info)
        total_info.extend(asked_prop_info)
        total_info.append(adapted_money_offer)
        total_info.append(adapted_money_asked)
        total_info.extend(initial_repr)
        total_info.extend(target_repr)

        total_info_np = np.array(total_info)

        self.last_state = np.array(total_info)

        return total_info_np

    def get_binary_representation(self, prop_list: List[BCs.Property], size: int):
        binary_repr = [0 for _ in range(size)]
        if len(prop_list) > 0:
            for prop in prop_list:
                binary_repr[prop.property_index] = 1

        return binary_repr

    # Meant for the first classification of actions
    def take_regular_decisions(self, state: MSs.RegularMonopolyState, action_list: List[MAs.ActionType]) -> List[MAs.ActionStructure]:
        adapted_state = self.form_regular_state(state)
        decisions = self.regular_actor.get_action(adapted_state)
        self.last_decision = np.copy(decisions)
        decision_structures: List[MAs.ActionStructure] = []

        for action in action_list:
            if action == MAs.ActionType.MakeTradeOffer:
                trade_section = decisions[0:61]
                decision_structures.append(self.make_trade_offer(trade_section))
            elif action == MAs.ActionType.ImproveProperty:
                improve_section = decisions[61:83]
                decision_structures.append(self.improve_property(improve_section))
            elif action == MAs.ActionType.SellHouseOrHotel:
                sell_section = decisions[83:105]
                decision_structures.append(self.sell_house_hotel(sell_section))
            elif action == MAs.ActionType.MortgageProperty:
                mortgage_section = decisions[105:133]
                decision_structures.append(self.mortgage_properties(mortgage_section))
            elif action == MAs.ActionType.FreeMortgage:
                free_section = decisions[133:161]
                decision_structures.append(self.free_mortgage(free_section))
            elif action == MAs.ActionType.ConcludeActions:
                conclude_section = decisions[161]
                decision_structures.append(self.conclude_actions(conclude_section))
            elif action == MAs.ActionType.UseGetOutOfJailCard:
                use_card_section = decisions[162]
                decision_structures.append(self.use_get_out_of_jail_card(use_card_section))
            elif action == MAs.ActionType.PayJailFine:
                pay_fine_section = decisions[163]
                decision_structures.append(self.pay_jail_fine(pay_fine_section))
            elif action == MAs.ActionType.BuyProperty:
                buy_section = decisions[164]
                decision_structures.append(self.buy_property(buy_section))

        return decision_structures

    # Meant for the second classificaction of actions available
    def take_trading_decisions(self, state: MSs.OfferActionMonopolyState, action_list: List[MAs.ActionType]) -> List[MAs.ActionStructure]:
        adapted_state = self.form_trading_state(state)
        decisions = self.trading_actor.get_action(adapted_state)
        self.last_decision = np.copy(decisions)
        decision_structures: List[MAs.ActionStructure] = []

        for action in action_list:
            if action == MAs.ActionType.ContinueInAuction:
                continue_section = decisions[1:3]
                decision_structures.append(self.continue_in_auction(continue_section))
            elif action == MAs.ActionType.AcceptTradeOffer:
                accept_section = decisions[0]
                decision_structures.append(self.accept_trade_offer(accept_section))

        return decision_structures

    #endregion AUX_FUNCTIONS