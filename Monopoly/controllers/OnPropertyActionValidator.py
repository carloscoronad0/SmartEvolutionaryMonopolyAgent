import Monopoly.models.BoardComponents as BCs
from Monopoly.models.PlayerModel import Player
from typing import List

MAX_IMPROVEMENTS = 5
MIN_IMPROVEMENTS = 0

class OnPropertyActionValidator:

    @staticmethod
    def _isSellHouseValid(valid_streets: List[BCs.StreetProperty], not_valid_streets: List[int]):
        not_valid_issue = len(not_valid_streets) == 0
        can_sell = []

        for street in valid_streets:
            can_sell.append(street._can_sell_house())

        can_sell_issue = all(can_sell)

        valid = not_valid_issue & can_sell_issue
        args = [(not_valid_issue, not_valid_streets), (can_sell_issue, can_sell)]

        return (valid, args)

    @staticmethod
    def _isBuyHouseValid(valid_streets: List[BCs.StreetProperty], not_valid_streets: List[int], player_money: int):
        not_valid_issue = len(not_valid_streets) == 0
        total_cost = []
        can_improve = []

        for street in valid_streets:
            total_cost.append(street.cost)
            can_improve.append(street._can_build_house())

        money_issue = sum(total_cost) <= player_money
        can_improve_issue = all(can_improve)

        valid = not_valid_issue & money_issue & can_improve_issue
        args = [(not_valid_issue, not_valid_streets), (money_issue, player_money), (can_improve_issue, can_improve)]

        return (valid, args)

    @staticmethod
    def _isTradeValid(valid_properties_offer: List[BCs.Property], valid_properties_asked: List[BCs.Property],
        not_valid_offered_properties: List[int], not_valid_asked_properties: List[int], 
        money_offer: int, money_asked: int, initial_player_money: int, target_player_money: int):

        # The properties to take part of the trade musn't have any buildings on them 
        offer_building_issue = [prop._is_unimproved() for prop in valid_properties_offer if prop.type == "street"]
        asked_building_issue = [prop._is_unimproved() for prop in valid_properties_asked if prop.type == "street"]

        # There shouldn't be any invalid properties in the transaction
        not_valid_offer_issue = len(not_valid_offered_properties) == 0
        not_valid_asked_issue = len(not_valid_asked_properties) == 0

        # The money offered and the money asked should be in the range of the amount each player has
        money_offer_issue = money_offer >= initial_player_money
        money_asked_issue = money_asked >= target_player_money

        # For the decision to be valid, all the issues must be passed succesfully
        valid = (offer_building_issue & asked_building_issue & not_valid_offer_issue & not_valid_asked_issue &
            money_offer_issue & money_asked_issue)

        # Specifications for the player, to identify which part of the decision was wrong
        args = [(offer_building_issue, valid_properties_offer), (asked_building_issue, valid_properties_asked), 
            (not_valid_offer_issue, not_valid_offered_properties), (not_valid_asked_issue, not_valid_asked_properties),
            (money_offer_issue, initial_player_money), (money_asked_issue, target_player_money)]
        
        return (valid, args)

    @staticmethod
    def _isMortgagePropertyValid(valid_properties: List[BCs.Property], not_valid_properties: List[int]):
        not_valid_issue = len(not_valid_properties) == 0
        unmortgaged = []
        unimproved = []

        for prop in valid_properties:
            unmortgaged.append(prop._is_unmortgaged())

            if prop.type == "street":
                unimproved.append(prop._is_unimproved())

        unmortgage_issue = all(unmortgaged)
        unimproved_issue = True
        if len(unimproved) > 0:
            unimproved_issue = all(unimproved)

        valid = not_valid_issue & unmortgage_issue & unimproved_issue
        args = [(not_valid_issue, not_valid_properties), (unmortgage_issue, unmortgaged), (unimproved_issue, unimproved)]

        return (valid, args)

    @staticmethod
    def _isFreePropertyFromMortgageValid(valid_properties: List[BCs.Property], not_valid_properties: List[int], player_money: int):
        not_valid_issue = len(not_valid_properties) == 0

        mortgaged = []
        cost = []

        for prop in valid_properties:
            mortgaged.append(prop._is_mortaged())
            cost.append(prop.free_mortgage)

        mortgaged_issue = all(mortgaged)
        total_cost_issue = sum(cost) <= player_money

        valid = not_valid_issue & mortgaged_issue & total_cost_issue
        args = [(not_valid_issue, not_valid_properties), (mortgaged_issue, mortgaged), (total_cost_issue, cost)]
                
        return (valid, args)

    @staticmethod
    def _isBuyPropertyValid(property_cost: int, player_money: int):
        money_issue = property_cost <= player_money

        return (money_issue, [(money_issue, property_cost)])

    @staticmethod
    def _isAuctionDecisionValid(player_money_offer: int, highest_money_offer: int, player_actual_money_amount: int):
        """
        The things that are necessary to validate for an auction decision are:
            If the player has the amount of money offered
            If the money offered is greater than the biggest amount offered up to the moment
        """
        has_the_money_issue = player_actual_money_amount >= player_money_offer
        greater_money_issue = player_money_offer > highest_money_offer

        args = [(has_the_money_issue, player_money_offer), (greater_money_issue, highest_money_offer)]

        return ((has_the_money_issue & greater_money_issue), args)