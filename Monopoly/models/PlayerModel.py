import Monopoly.models.BoardComponents as BCs
import Monopoly.models.MonopolyActions as MAs
import numpy as np

from Monopoly.models.AgentModels.AgentModel import Agent
from typing import List, Tuple

class Player:
    def __init__(self, player_id: int, money: int, agent: Agent):
        self.player_id = player_id
        self.position = 0
        self.money = money
        self.in_jail = False
        self.out_of_jail_card = False
        self.agent = agent
        self.properties = []
        self.bankrupted = False
    
    #region GAME_ACTIONS

    def advance_on_table(self, number_of_squares: int, board_size: int) -> int:
        """
        Function used for moving the player forward in the table

        It first updates it's position and returns the new position for the Monopoly Game to use if
        necessary
        """
        # Updates it's position
        self.position = (self.position + number_of_squares) % board_size
        # Returns the new position
        return self.position

    def pay_transaction(self, amount_to_pay: int, transaction_details: str = "") -> int:
        """
        Used when player is involved in transactions that require money exhange with the bank
        """
        # Reduces the player's money amount by the received parameter
        self.money -= amount_to_pay
        print(f"On player {self.player_id}")
        print(transaction_details)
        return amount_to_pay

    def receive_payment(self, amount_received: int, payment_details: str = ""):
        """
        Function used when the player receives a payment for some reason:
            Rent
            Go square
            Community card

        It simply adds the amount to receive to the money the Player posses
        """
        self.money += amount_received

    def add_property(self, new_property: BCs.Property):
        """
        This function's purpose it's just to add new properties bought or traded to the Player's
        property list
        """
        self.properties.append(new_property)

    def remove_property(self, removed_property: BCs.Property):
        """
        This function's purpose it's to remove properties which the Player has sold or traded, 
        it's suposed to receive a pointer to the memory space with the object, same as the one contained in
        the player's properties list, so there should be no problem in removing the object, as they
        are the same.
        """
        self.properties.remove(removed_property)

    def enough_money(self, amount: int) -> bool:
        return self.money >= amount

    def is_bankrupt(self, amount: int) -> bool:
        property_money: int = 0

        for prop in self.properties:
            property_money += prop.mortgage

            if prop.type == "street":
                property_money += round(prop.buildings * 0.5)
        
        total_net_value = self.money + property_money

        is_bankrupt = total_net_value >= amount
        return is_bankrupt

    #endregion GAME_ACTIONS

    #region ASK_AGENT
    
    def actions(self, valid_actions: List[MAs.ActionType], state) -> List[MAs.ActionStructure]:
        pass

    def inform_decision_quality(self, decisions_to_inform: List[MAs.ActionType], args_list):
        pass

    #endregion ASK_AGENT