from Monopoly.models.AgentModels.AgentModel import Agent
from typing import List, Tuple

import numpy as np

class SmartAgent(Agent):
    def __init__(self):
        pass

    def take_decisions(self):
        pass

    # Meant for the first classification of actions
    def actions_initiated_by_player(self) -> Tuple[Tuple[int, np.ndarray, np.ndarray, int, int], np.ndarray, np.ndarray, np.ndarray, np.ndarray, bool, bool, bool, bool]:
        pass

    # Meant for the second classificaction of actions available
    def actions_initiated_by_other_entity(self) -> Tuple[bool, int]:
        pass

    #region ACTIONS_INITIATED_BY_PLAYER

    def make_trade_offer(self, trade_binary_representation: np.ndarray) -> Tuple[int, np.ndarray, np.ndarray, int, int]:
        """
        Punish if: 
            - Property is not Owned by the player
            - Property has houses or a hotel

        Format:
            - [Offered Properties] -> 28
            - [Wished Properties] -> 28
            - [Money offered] -> 1 : Percentage * own Money
            - [Wished Money] -> 1 : Percentage * own Money
            - [Target Player] -> 3 : [PA, PB, PC]
        """

        property_offering = trade_binary_representation[0:27].copy()
        property_asked = trade_binary_representation[28:55].copy()
        percentage_money_offered = trade_binary_representation[56].copy()
        percentage_money_asked = trade_binary_representation[57].copy()
        player = trade_binary_representation[58:60].copy()

        print(f"{property_offering}\n{property_asked}\n{percentage_money_offered}\n{percentage_money_asked}\n{player}")

        offer = np.where(property_offering == 1)
        asked = np.where(property_asked == 1)
        money_offer = self._transform_money(self.money, percentage_money_offered)
        money_ask = self._transform_money(self.money, percentage_money_asked)
        target_player_id = np.where(player == 1)

        return (target_player_id, offer, asked, money_offer, money_ask)

    def improve_property(self, streets_binary: np.ndarray) -> np.ndarray:
        return np.where(streets_binary == 1)

    def sell_house_hotel(self, streets_binary: np.ndarray) -> np.ndarray:
        return np.where(streets_binary == 1)
    
    def mortgage_properties(self, mortgage_binary: np.ndarray) -> np.ndarray:
        return np.where(mortgage_binary == 1)

    def free_mortgage(self, free_binary: np.ndarray) -> np.ndarray:
        return np.where(free_binary == 1)

    def conclude_actions(self, conclude_binary: int) -> bool:
        return conclude_binary > 0

    def use_get_out_of_jail_card(self, use_card_biinary: int) -> bool:
        return use_card_biinary > 0

    def pay_jail_fine(self, pay_fine_binary: int) -> bool:
        return pay_fine_binary > 0

    def buy_property(self, buy_binary: int) -> bool:
        return buy_binary > 0

    #endregion ACTIONS_INITIATED_BY_PLAYER

    #region ACTIONS_INITIATED_BY_OTHER_ENTITY

    def accept_trade_offer(self, accept_binary: int) -> bool:
        return accept_binary > 0

    def continue_in_auction(self, continue_info: Tuple[int, int]):
        pass

    #endregion ACTIONS_INITIATED_BY_OTHER_ENTITY

    #region AUX_FUNCTIONS

    @staticmethod
    def _transform_money(baseline_money: float, percentage: float) -> int:
        return int(percentage * baseline_money)

    #endregion AUX_FUNCTIONS