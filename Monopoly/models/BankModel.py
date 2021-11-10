import Monopoly.models.BoardComponents as p
import Monopoly.models.TransactionsModels as tm
import numpy as np

from Monopoly.models.PlayerModel import Player
from typing import List, Tuple

MAX_IMPROVEMENTS = 5
MIN_IMPROVEMENTS = 0

class Bank:
    def __init__(self, properties: List[p.Property], streets: List[p.StreetProperty]):
        self.properties = properties
        self.streets = streets

    #region TRANSACTIONS

    def trade_transaction(self, initial_player: Player, target_player: Player, properties_offer: np.ndarray, 
        properties_asked: np.ndarray, money_offered: int, money_asked: int) -> tm.TradeTransaction:

        # get properties from players
        (offer, not_valid_offer) = self._get_indicated_properties(initial_player.id, properties_offer)
        (asked, not_valid_asked) = self._get_indicated_properties(target_player.id, properties_asked)

        if (len(not_valid_offer) > 0) | (len(not_valid_asked) > 0):
            return None

        # valdiate the players can afford the transaction
        if initial_player.enough_money(money_offered) & target_player.enough_money(money_asked):
            is_successful = False
            comment = ""

            # ask the target player to take a decision about the offering
            (decision, _) = target_player.actions_initiated_by_other_entity()

            if decision:
                comment = "Trade accepted by player " + target_player.id 

                # Properties exchange
                for prop in offer:
                    self.change_owner(prop, initial_player, target_player)

                for prop in asked:
                    self.change_owner(prop, target_player, initial_player)

                # Money exchange
                money_from_initial = initial_player.pay_transaction(money_offered)
                money_from_target = target_player.pay_transaction(money_asked)

                initial_player.receive_payment(money_from_target)
                target_player.receive_payment(money_from_initial)

                # Trasanction successful
                is_successful = True
            else:
                comment = "Trade rejected by player " + target_player.id

            return tm.TradeTransaction(is_successful, initial_player.id, "Trade", comment, money_offered, 
                target_player.id, money_asked, properties_offer, properties_asked)

        return None

    def auction_transaction(self):
        pass

    def improve_property_transaction(self, player: Player, properties: np.ndarray):
        (to_improve, not_valid) = self._get_indicated_properties(player.id, properties)

        # Has to change to indicated player that the cause of the error is the selection
        # of unowned properties
        if len(not_valid) > 0:
            return None

        
    
    #endregion TRASANCTIONS

    #region AUX_FUNCTIONS

    def _get_indicated_properties(self, player_id: int, properties_index: List[int]) -> Tuple[List[p.Property], List[int]]:
        valid_properties = []
        not_valid_properties = []

        # For each indicated property
        for i in properties_index:
            # If the owner is the player (Validating ownership)
            if self.properties[i].owner is player_id:
                # Add it to the list
                valid_properties.append(self.properties[i])
            else: # Else end the proceedure 
                not_valid_properties.append(i)

        return (valid_properties, not_valid_properties)

    def change_owner(self, property: p.Property, old_owner: Player, new_owner: Player):
        old_owner.remove_property(property)
        property.owner = new_owner.id
        new_owner.add_property(property)

    #endregion AUX_FUNCTIONS
