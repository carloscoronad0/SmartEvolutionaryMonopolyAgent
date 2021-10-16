import Monopoly.models.Properties as p
import numpy as np

from Monopoly.models.AgentModels.AgentModel import Agent
from Monopoly.controllers.OnPropertyActionValidator import PropertyActionValidator as PAV
from typing import List, Tuple

MAX_IMPROVEMENTS = 5
MIN_IMPROVEMENTS = 0


class Player:
    def __init__(self, id: int, money: int, agent: Agent, properties: List[p.Property] = [], 
        streets: List[p.StreetProperty] = []) -> None:
        self.id = id
        self.position = 0
        self.properties = properties
        self.streets = streets
        self.money = money
        self.get_out_of_jail_card = None
        self.agent = agent
        
    def do_actions(self):
        pass

    # ----------------------------------------
    # Agent actions
    
    def make_trade_offer(self, player_id: np.ndarray, property_offering: np.ndarray, property_asked: np.ndarray,
        money_offered: np.ndarray, money_asked: np.ndarray) -> Tuple[int, np.ndarray, np.ndarray, int, int]:

        player = np.where(player_id == 1)
        (found, not_found) = self._mapping_from_binary_to_properties(self.properties, property_offering, self._get_property_index)
        valids = []

        for prop in found:
            if PAV._validate_sell(prop):
                valids.append(prop.index)

        if len(valids) == len(found):
            money_off = self._transform_money(money_offered, self._calculate_properties_net_value(found))
            return (player, valids, property_asked, money_off, money_asked)
        else:
            return None

    def improve_property(self, streets_binary: np.ndarray) -> np.ndarray:
        (found, not_found) = self._mapping_from_binary_to_properties(self.streets, streets_binary, self._get_street_index)
        valids = []

        for prop in found:
            if prop.set_completed:
                color_group = self.get_color_group(prop.street_color)
                if PAV._validate_street_improvement(prop, color_group):
                    valids.append(prop.index)

        if len(valids) == len(found):
            return np.array(valids)
        else:
            return None

    def sell_house_hotel(self, streets_binary: np.ndarray) -> np.ndarray:
        (found, not_found) = self._mapping_from_binary_to_properties(self.streets, streets_binary, self._get_street_index)
        valids = []

        for prop in found:
            if prop.set_completed:
                color_group = self.get_color_group(prop.street_color)
                if PAV._validate_street_breakdown(prop, color_group):
                    valids.append(prop.index)

        if len(valids) == len(found):
            return np.array(valids)
        else:
            return None

    def mortgage_properties(self, mortgage_binary: np.ndarray) -> np.ndarray:
        (found, not_found) = self._mapping_from_binary_to_properties(self.properties , mortgage_binary, self._get_property_index)
        valids = [prop.index for prop in found if PAV._validate_mortgage(prop)]
        
        if len(valids) == len(found):
            return np.array(valids)
        else:
            return None

    def free_mortgage(self, free_binary: np.ndarray) -> np.ndarray:
        (found, not_found) = self._mapping_from_binary_to_properties(self.properties , free_binary, self._get_property_index)
        valids = []
        aux_money = self.money

        for prop in found:
            if PAV._validate_free_mortgage(aux_money, prop):
                valids.append(prop.index)
                aux_money -= prop.free_mortgage
        
        if len(valids) == len(found):
            return np.array(valids)
        else:
            return None

    def conclude_actions(self, conclude_binary: int) -> bool:
        return conclude_binary > 0

    def use_get_out_of_jail_card(self, use_card_biinary: int) -> bool:
        return use_card_biinary > 0

    def pay_jail_fine(self, pay_fine_binary: int) -> bool:
        return pay_fine_binary > 0

    def accept_trade_offer(self, accept_binary: int) -> bool:
        return accept_binary > 0

    def buy_property(self, buy_binary: int) -> bool:
        return buy_binary > 0

    # --------------------------------------------------
    # Game actions

    def advance(self, number_of_squares: int) -> int:
        self.position = self.position + number_of_squares
        return self.position

    def pay_service(self, amount_to_pay: int, service: str) -> int:
        self.money = self.money - amount_to_pay
        
        if self.is_bankrupt():
            return -1
        else:
            return amount_to_pay

    def _get_property_index(self, property: p.Property) -> int:
        return property.property_index

    def _get_street_index(self, street: p.StreetProperty) -> int:
        return street.street_index

    @staticmethod
    def _mapping_from_binary_to_properties(properties: List[p.Property] ,binary_representation: np.ndarray, get_index) -> Tuple[List[p.Property], np.ndarray]:
        print("Mapping properties")
        properties_indexes = np.where(binary_representation == 1)
        owned_properties = []

        for prop in properties:
            i = get_index(prop)
            if properties_indexes.__contains__(i):
                print(f"Found {prop} of index {i}")
                owned_properties.append(prop)
                properties_indexes.remove(i)

        # returns the properties that the player owns, the properties found are removed from 
        # properties_indexes, so the list is returned to represent the ones that were not found
        return (owned_properties, properties_indexes)
    
    def _get_color_group(self, color: str) -> List[p.StreetProperty]:
        return [prop for prop in self.streets if prop.street_color == color]

    @staticmethod
    def _calculate_properties_net_value(properties: List[p.Property]):
        return sum([prop.cost for prop in properties])

    @staticmethod
    def _transform_money(money_identificator: np.ndarray, net_value: int):
        # +1 because the ponderations are 1/1 1/2 1/3 1/4 and indexes start from 0
        # so +1 is required to meet a right ponderation
        ponderation = sum(np.where(money_identificator == 1)) + 1

        return net_value * (1/ponderation)