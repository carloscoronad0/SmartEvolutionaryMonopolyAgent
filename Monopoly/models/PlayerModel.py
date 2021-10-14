import Monopoly.models.Properties as p
from Monopoly.models.AgentModels.AgentModel import Agent
from typing import List


class Player:
    def __init__(self, id: int, money: int, agent: Agent, properties: List[p.Property] = []) -> None:
        self.id = id
        self.position = 0
        self.properties = properties
        self.money = money
        self.get_out_of_jail_card = None
        self.agent = agent
        
    def do_actions(self):
        pass

    # ----------------------------------------
    # Agent actions
    
    def make_trade_offer(self):
        pass

    def improve_property(self) -> p.StreetProperty:
        pass

    def sell_house_hotel(self) -> p.StreetProperty:
        pass

    def sell_property(self) -> p.Property:
        pass

    def mortgage_property(self) -> p.Property:
        pass

    def free_mortgage(self) -> p.Property:
        pass

    def conclude_actions(self) -> bool:
        pass

    def use_get_out_of_jail_card(self) -> bool:
        pass

    def pay_jail_fine(self) -> bool:
        pass

    def accept_trade_offer(self) -> bool:
        pass

    def buy_property(self) -> bool:
        pass

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

    def _is_bankrupt(self) -> bool:
        if self.money < 0:
            if len([a for a in self.properties if a.mortgage_state == False]) > 0:
                pass
        else:
            return False 