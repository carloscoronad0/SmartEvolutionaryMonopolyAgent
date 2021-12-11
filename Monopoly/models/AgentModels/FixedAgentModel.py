from Monopoly.models.AgentModels.BaseAgentModel import Agent
from typing import List

import Monopoly.models.BoardComponents as BCs
import Monopoly.models.MonopolyActions as MAs
import Monopoly.models.MonopolyStates as MSs
import random

COLORS_INFO = [('purple',2,1),('lightblue',3,1),('violet',3,2),('orange',3,2),('red',3,3),
    ('yellow',3,3),('darkgreen',3,4),('darkblue',2,4)]
# PRIORITIZE = ["railroad","orange"]

MUST_SELL = [MAs.ActionType.SellHouseOrHotel, MAs.ActionType.MortgageProperty]

MONEY_BALANCE = 200

class FixedAgent(Agent):
    def __init__(self, agent_id: int, prioritize_list: List[str], avoid_list: List[str]):
        super().__init__(agent_id, "fixed")
        self.must_sell = False
        self.prioritize = prioritize_list
        self.avoid = avoid_list

    def take_decisions(self, valid_actions: List[MAs.ActionType], state: MSs.MonopolyState) -> List[MAs.ActionStructure]:
        decisions: List[MAs.ActionStructure] = []
        # print(f"Taking decisions in player {self.id_in_game}")

        if MUST_SELL == valid_actions:
            self.must_sell = True
            # print("Must sell")

        for decision in valid_actions:
            res = self.take_decision(decision, state)
            if res != None:
                decisions.append(res)

        self.must_sell = False
        self.last_action_initialization = state.stateType

        return decisions
    
    def decision_quality(self, resulting_state, decisions_to_inform, args_list):
        if self.last_action_initialization == MAs.ActionInitializationType.InitiatedByOtherEntity:
            (p_prop_num, mn_op_prop, num_clr_compl, h_build, pl_mny, mn_op_mny) = self.get_reward_parameters_from_trade(resulting_state)
        else:
            (p_prop_num, mn_op_prop, num_clr_compl, h_build, pl_mny, mn_op_mny) = self.get_reward_parameters_from_regular(resulting_state)

        reward = self.reward_function(p_prop_num, mn_op_prop, num_clr_compl, h_build, pl_mny, mn_op_mny)
        self.rewards_in_game += reward
        self.last_action_initialization = None

    def clone(self, ag_id):
        clone = type(self)(agent_id = ag_id,
                            prioritize_list = self.prioritize,
                            avoid_list = self.avoid)
        clone.agent_id = ag_id
        clone.agent_type = "fixed"
        clone.must_sell = False

        return clone

    def take_decision(self, desicion_to_take: MAs.ActionType, state) -> MAs.ActionStructure:
        if desicion_to_take == MAs.ActionType.MakeTradeOffer:
            return self.make_trade_offer(state)

        elif desicion_to_take == MAs.ActionType.ContinueInAuction:
            return self.continue_in_auction(state)

        elif desicion_to_take == MAs.ActionType.ImproveProperty:
            return self.improve_property(state)

        elif desicion_to_take == MAs.ActionType.SellHouseOrHotel:
            return self.sell_house_hotel(state)

        elif desicion_to_take == MAs.ActionType.MortgageProperty:
            return self.mortgage_properties(state)

        elif desicion_to_take == MAs.ActionType.FreeMortgage:
            return self.free_mortgage(state)

        elif desicion_to_take == MAs.ActionType.ConcludeActions:
            return self.conclude_actions(state)

        elif desicion_to_take == MAs.ActionType.UseGetOutOfJailCard:
            return self.use_get_out_of_jail_card(state)

        elif desicion_to_take == MAs.ActionType.PayJailFine:
            return self.pay_jail_fine(state)

        elif desicion_to_take == MAs.ActionType.AcceptTradeOffer:
            return self.accept_trade_offer(state)

        elif desicion_to_take == MAs.ActionType.BuyProperty:
            return self.buy_property(state)

    #region ACTIONS_INITIATED_BY_PLAYER

    def make_trade_offer(self, state: MSs.RegularMonopolyState) -> MAs.TradeActionStructure:
        player = None
        
        for pl in state.playersInGame:
            if pl.player_id == self.id_in_game:
                player = pl

        one_of_the_set = []
        two_of_the_set = []

        missing = {}

        for prop in player.properties:
            if prop.type == "street":
                if not prop.set_completed:
                    if one_of_the_set.__contains__(prop.street_color):
                        missing[prop.street_color].append(prop.property_index)
                        one_of_the_set.remove(prop.street_color)
                        two_of_the_set.append(prop.street_color)
                    else:
                        missing[prop.street_color] = []
                        missing[prop.street_color].append(prop.property_index)
                        one_of_the_set.append(prop.street_color)

        for prop in state.propertiesInGame:
            if (prop.owner != None) & (prop.type == "street"):
                if (prop.owner.player_id != self.id_in_game):
                    prop_ticket = self.get_property_ticket(prop)
                    if self.prioritize.__contains__(prop_ticket) | (two_of_the_set.__contains__(prop_ticket)):
                        can_offer = [color for color in one_of_the_set if not self.prioritize.__contains__(color)]
                        if len(can_offer) > 0:
                            rnd_idx = random.randint(0, (len(can_offer) - 1))
                            return MAs.TradeActionStructure(MAs.ActionType.MakeTradeOffer,
                                missing[one_of_the_set[rnd_idx]], [prop.property_index],
                                0, 0, prop.owner.player_id)

        return None

    def improve_property(self, state: MSs.RegularMonopolyState) -> MAs.PropertyActionStructure:
        over_optimum = []
        for prop in state.propertiesInGame:
            if (prop.owner != None) & (prop._is_unmortgaged()) & (prop.type == "street"):
                if (prop.owner.player_id == self.id_in_game) & ((prop.owner.money - prop.house_price) > MONEY_BALANCE):
                    if (prop.buildings < 3):
                        return MAs.PropertyActionStructure(MAs.ActionType.ImproveProperty, [prop.street_index],
                            MAs.PropertyType.Street)
                    else:
                        over_optimum.append(prop.street_index)

        if len(over_optimum) > 0:
            rnd_idx = random.randint(0, (len(over_optimum) - 1))
            return MAs.PropertyActionStructure(MAs.ActionType.ImproveProperty, [over_optimum[rnd_idx]],
                MAs.PropertyType.Street)

        return None

    def sell_house_hotel(self, state: MSs.RegularMonopolyState) -> MAs.PropertyActionStructure:
        optimum_buildings = []

        if self.must_sell:
            for prop in state.propertiesInGame:
                if (prop.owner != None) & (prop.type == "street"):
                    if (prop.owner.player_id == self.id_in_game) & (not prop._is_unimproved()):
                        if prop.buildings < 3:
                            return MAs.PropertyActionStructure(MAs.ActionType.SellHouseOrHotel, [prop.street_index],
                                MAs.PropertyType.Street)
                        else:
                            optimum_buildings.append(prop.street_index)

            if len(optimum_buildings) > 0:
                rnd_idx = random.randint(0, (len(optimum_buildings) - 1))
                return MAs.PropertyActionStructure(MAs.ActionType.SellHouseOrHotel, [optimum_buildings[rnd_idx]],
                    MAs.PropertyType.Street)
            else:
                return MAs.PropertyActionStructure(MAs.ActionType.SellHouseOrHotel, [],
                    MAs.PropertyType.Street)

        return None
    
    def mortgage_properties(self, state: MSs.RegularMonopolyState) -> MAs.PropertyActionStructure:
        not_completed_streets = []
        completed_streets = []

        if self.must_sell:
            for prop in state.propertiesInGame:
                if (prop.owner != None) & (prop._is_unmortgaged()):
                    if prop.owner.player_id == self.id_in_game:
                        if prop.type == "street":
                            if prop._is_unimproved():
                                if prop.set_completed:
                                    completed_streets.append(prop.property_index)
                                else:
                                    not_completed_streets.append(prop.property_index)
                        else:
                            return MAs.PropertyActionStructure(MAs.ActionType.MortgageProperty, [prop.property_index],
                                MAs.PropertyType.Property)

            if len(not_completed_streets) > 0:
                rnd_idx = random.randint(0, (len(not_completed_streets) - 1))
                return MAs.PropertyActionStructure(MAs.ActionType.MortgageProperty, [not_completed_streets[rnd_idx]],
                    MAs.PropertyType.Property)
            elif len(completed_streets) > 0:
                rnd_idx = random.randint(0, (len(completed_streets) - 1))
                return MAs.PropertyActionStructure(MAs.ActionType.MortgageProperty, [completed_streets[rnd_idx]],
                    MAs.PropertyType.Property)
            else:
                return MAs.PropertyActionStructure(MAs.ActionType.MortgageProperty, [], MAs.PropertyType.Property)

        return None

    def free_mortgage(self, state: MSs.RegularMonopolyState) -> MAs.PropertyActionStructure:
        for prop in state.propertiesInGame:
            if (prop.owner != None) & (prop._is_mortaged()):
                if (prop.owner.player_id == self.id_in_game) & ((prop.owner.money - prop.free_mortgage) > MONEY_BALANCE):
                    return MAs.PropertyActionStructure(MAs.ActionType.FreeMortgage, [prop.property_index],
                        MAs.PropertyType.Property)

        return None
                        
    def conclude_actions(self, state: MSs.RegularMonopolyState) -> MAs.BinaryActionStructure:
        return MAs.BinaryActionStructure(MAs.ActionType.ConcludeActions, True)

    def use_get_out_of_jail_card(self, state: MSs.RegularMonopolyState) -> MAs.BinaryActionStructure:
        return MAs.BinaryActionStructure(MAs.ActionType.UseGetOutOfJailCard, True)

    def pay_jail_fine(self, state: MSs.RegularMonopolyState) -> MAs.BinaryActionStructure:
        for pl in state.playersInGame:
            if (pl.player_id != self.id_in_game) and (pl.sets_completed > 0):
                return MAs.BinaryActionStructure(MAs.ActionType.PayJailFine, False)

        return MAs.BinaryActionStructure(MAs.ActionType.PayJailFine, True)

    def buy_property(self, state: MSs.RegularMonopolyState) -> MAs.BinaryActionStructure:
        player_pos = 0
        player_money = 0
        for pl in state.playersInGame:
            if pl.player_id == self.id_in_game:
                player_pos = pl.position
                player_money = pl.money
                break
        
        property_to_buy = None
        for prop in state.propertiesInGame:
            if prop.index == player_pos:
                property_to_buy = prop
                break

        response = False
        prop_ticket = self.get_property_ticket(property_to_buy)

        if (self.prioritize.__contains__(prop_ticket)):
            response = True
        elif (not self.avoid.__contains__(prop_ticket)) & ((player_money - property_to_buy.cost) >= MONEY_BALANCE):
            response = True

        return MAs.BinaryActionStructure(MAs.ActionType.BuyProperty, response)
        
    #endregion ACTIONS_INITIATED_BY_PLAYER

    #region ACTIONS_INITIATED_BY_OTHER_ENTITY

    def accept_trade_offer(self, state: MSs.OfferActionMonopolyState) -> MAs.BinaryActionStructure:
        net_value = 0
        for prop in state.targetPlayer.properties:
            if not state.askedProperties.__contains__(prop):
                net_value += prop.cost

        for prop in state.offerdProperties:
            net_value += prop.cost

        net_value += (state.targetPlayer.money - state.moneyAsked + state.moneyOffer)

        res = net_value >= state.targetPlayer.net_value()

        return MAs.BinaryActionStructure(MAs.ActionType.AcceptTradeOffer, res)

    def continue_in_auction(self, state: MSs.OfferActionMonopolyState) -> MAs.AuctionActionStructure:
        prop_in_auction = state.offerdProperties[0]

        response = False
        prop_ticket = self.get_property_ticket(prop_in_auction)
        if (self.prioritize.__contains__(prop_ticket)) & (state.moneyAsked <= round(prop_in_auction.cost + (prop_in_auction.cost * 0.5))):
            response = True
        elif (self.avoid.__contains__(prop_ticket)) & (state.moneyAsked < prop_in_auction.cost) & ((state.targetPlayer.money - state.moneyAsked) >= MONEY_BALANCE):
            response = True
        elif (state.moneyAsked <= round(prop_in_auction.cost + (prop_in_auction.cost * 0.25))) & ((state.targetPlayer.money - state.moneyAsked) >= MONEY_BALANCE):
            response = True

        return MAs.AuctionActionStructure(MAs.ActionType.ContinueInAuction, response, state.moneyAsked + 1)

    #endregion ACTIONS_INITIATED_BY_OTHER_ENTITY

    def get_property_ticket(self, property_to_form_ticket):
        prop_ticket = ""
        if property_to_form_ticket.type != "street":
            prop_ticket = property_to_form_ticket.type
        else:
            prop_ticket = property_to_form_ticket.street_color

        return prop_ticket