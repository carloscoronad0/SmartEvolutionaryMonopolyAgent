from Monopoly.models.AgentModels.BaseAgentModel import Agent
from Monopoly.models.PlayerModel import Player
from typing import List, Tuple

import numpy as np
import Monopoly.models.BoardComponents as BCs
import Monopoly.models.MonopolyActions as MAs
import Monopoly.models.MonopolyStates as MSs

class UserAgent(Agent):
    def __init__(self, agent_id: int):
        super().__init__(agent_id, "user")

    def take_decisions(self, valid_decisions_to_take: List[MAs.ActionType], state: MSs.MonopolyState) -> List[MAs.ActionStructure]:

        if state.stateType == MAs.ActionInitializationType.InitiatedByPlayer:
            self.display_regular_game_state(state)
        else:
            self.display_offer_action_game_state(state)


        decisions: List[MAs.ActionStructure] = []

        for decision in valid_decisions_to_take:
            res = self.take_decision(decision)
            if res != None:
                decisions.append(res)

        return decisions

    def decision_quality(self, resulting_state: MSs.MonopolyState, decisions_to_inform: List[MAs.ActionType], 
        args_list):
        for i in range(len(decisions_to_inform)):
            print("--------------------")
            print(decisions_to_inform[i])
            print(args_list[i])

        if resulting_state.stateType == MAs.ActionInitializationType.InitiatedByOtherEntity:
            (p_prop_num, mn_op_prop, num_clr_compl, h_build, pl_mny, mn_op_mny) = self.get_reward_parameters_from_trade(resulting_state)
        elif resulting_state.stateType == MAs.ActionInitializationType.InitiatedByPlayer:
            (p_prop_num, mn_op_prop, num_clr_compl, h_build, pl_mny, mn_op_mny) = self.get_reward_parameters_from_regular(resulting_state)

        reward = self.reward_function(p_prop_num, mn_op_prop, num_clr_compl, h_build, pl_mny, mn_op_mny)
        self.rewards_in_game += reward

    def clone(self, ag_id):
        clone = type(self)(agent_id=ag_id)
        clone.agent_id = ag_id
        clone.agent_type = "user"

    def take_decision(self, desicion_to_take: MAs.ActionType) -> MAs.ActionStructure:
        if desicion_to_take == MAs.ActionType.MakeTradeOffer:
            return self.take_trade_decision("Trade decision valid", MAs.ActionType.MakeTradeOffer)

        elif desicion_to_take == MAs.ActionType.ContinueInAuction:
            return self.take_auction_decision("Participating in auction", MAs.ActionType.ContinueInAuction)

        elif desicion_to_take == MAs.ActionType.ImproveProperty:
            return self.take_property_decision("Decision to improve property, only indexes from 0 to 21", 
                MAs.ActionType.ImproveProperty, MAs.PropertyType.Street)

        elif desicion_to_take == MAs.ActionType.SellHouseOrHotel:
            return self.take_property_decision("Decision to unimprove property, only indexes from 0 to 21", 
                MAs.ActionType.SellHouseOrHotel, MAs.PropertyType.Street)

        elif desicion_to_take == MAs.ActionType.MortgageProperty:
            return self.take_property_decision("Decision to mortgage property, only indexes from 0 to 27", 
                MAs.ActionType.MortgageProperty, MAs.PropertyType.Property)

        elif desicion_to_take == MAs.ActionType.FreeMortgage:
            return self.take_property_decision("Decision to unmortgage property, only indexes from 0 to 27", 
                MAs.ActionType.FreeMortgage, MAs.PropertyType.Property)

        elif desicion_to_take == MAs.ActionType.ConcludeActions:
            return self.take_binary_decision("Conclude actions", MAs.ActionType.ConcludeActions)

        elif desicion_to_take == MAs.ActionType.UseGetOutOfJailCard:
            return self.take_binary_decision("Use get out of jail card", MAs.ActionType.UseGetOutOfJailCard)

        elif desicion_to_take == MAs.ActionType.PayJailFine:
            return self.take_binary_decision("Pay jail fine", MAs.ActionType.PayJailFine)

        elif desicion_to_take == MAs.ActionType.AcceptTradeOffer:
            return self.take_binary_decision("Accept trade offer", MAs.ActionType.AcceptTradeOffer)

        elif desicion_to_take == MAs.ActionType.BuyProperty:
            return self.take_binary_decision("Buy property", MAs.ActionType.BuyProperty)

    def take_auction_decision(self, info_to_display: str, action_type: MAs.ActionType):
        print("\n---------------------------------------------\n")
        print(info_to_display)

        print("Enter 1 to continue, 0 to retire: ")
        res = int(input()) > 0

        if res:
            print("Enter the money offer: ")
            money_offer = int(input())

            return MAs.AuctionActionStructure(action_type, res, money_offer)
        else:
            return None

    def take_trade_decision(self, info_to_display: str, action_type: MAs.ActionType):
        print("\n---------------------------------------------\n")
        print(info_to_display)

        print("\nOFFER\n")
        offered_idxs = self.get_indexes()
        print("Money: ")
        money_offer = int(input())
        print("\nASKED\n")
        asked_idxs = self.get_indexes()
        print("Money: ")
        money_asked = int(input())

        print("PLAYER ID: ")
        player_id = int(input())

        if player_id < 0:
            return None
        else:
            return MAs.TradeActionStructure(action_type, offered_idxs, asked_idxs, money_offer, money_asked, player_id)

    def take_property_decision(self, info_to_display: str, action_type: MAs.ActionType, property_type: MAs.PropertyType):
        print("\n---------------------------------------------\n")
        print(info_to_display)
        idxs = self.get_indexes()
            
        if len(idxs) < 1:
            return None
        else:
            return MAs.PropertyActionStructure(action_type, idxs, property_type)

    def get_indexes(self) -> List[int]:
        indexes: List[int] = []
        print("Enter -1 to terminate")
        print("Please enter the index: ")
        res = int(input())

        while res >= 0:
            if not indexes.__contains__(res):
                print("ADDED")
                indexes.append(res)
            print("Please enter the index: ")
            res = int(input())

        return indexes

    def take_binary_decision(self, info_to_display: str, action_type: MAs.ActionType) -> bool:
        print("\n---------------------------------------------\n")
        print(info_to_display)
        print("Please enter 1 to Accept, 0 to decline: ")
        res = int(input()) > 0

        return MAs.BinaryActionStructure(action_type, res)

    def display_offer_action_game_state(self, state: MSs.OfferActionMonopolyState):
        print(f"This agent is {self.agent_id}")
        
        if state.initialPlayer != None:
            for player_prop in state.initialPlayer.properties:
                self.display_property_info(player_prop)

        for own_prop in state.targetPlayer.properties:
            self.display_property_info(own_prop)

        for off_prop in state.offerdProperties:
            self.display_property_info(off_prop)

        for ask_prop in state.askedProperties:
            self.display_property_info(ask_prop)

        print(f"MONEY OFFER: {state.moneyOffer}")
        print(f"MONEY ASKED: {state.moneyAsked}")

    def display_regular_game_state(self, state: MSs.RegularMonopolyState):
        print(f"Player in turn: {state.playerInTurnId}")
        print(f"This agent is {self.agent_id}")
        for p in state.playersInGame:
            self.display_player_info(p)

        for prop in state.propertiesInGame:
            self.display_property_info(prop)

    def display_player_info(self, player: Player):
        print("\n---------------------------------------------\n")
        print(player.player_info())

    def display_property_info(self, property_to_display: BCs.Property):
        if property_to_display.owner != None:
            property_owner = property_to_display.owner.player_id
        else:
            property_owner = -1 # To indicate it has no owner

        print("\n---------------------------------------------\n")
        print(f"Property owner: {property_owner}")
        print(property_to_display)