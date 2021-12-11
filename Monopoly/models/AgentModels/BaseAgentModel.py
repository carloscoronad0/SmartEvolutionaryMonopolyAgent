from abc import ABC, abstractmethod
from Monopoly.models import MonopolyStates as MSs

class Agent(ABC):
    def __init__(self, agent_id: int, agent_type: str):
        self.agent_id = agent_id
        self.agent_type = agent_type
        self.last_action_initialization = None
        self.id_in_game = -1
        self.rewards_in_game = 0
        self.reward_count = 0

    @abstractmethod
    def take_decisions(self, valid_actions, state):
        pass
    
    @abstractmethod
    def decision_quality(self, resulting_state, decisions_to_inform, args_list):
        pass

    @abstractmethod
    def clone(self, agent_id):
        pass

    def get_reward_parameters_from_trade(self, state: MSs.OfferActionMonopolyState):
        player_property_number = 0
        mean_op_property = 0
        num_color_completed = 0
        house_build = 0
        player_money = 0
        mean_op_money = 0

        if state.initialPlayer != None:
            mean_op_property = len(state.initialPlayer.properties)
            mean_op_money = state.initialPlayer.money

        if state.targetPlayer != None:
            player_property_number = len(state.targetPlayer.properties)
            player_money = state.targetPlayer.money
            num_color_completed = state.targetPlayer.sets_completed

            for prop in state.targetPlayer.properties:
                if prop.type == "street":
                    house_build += prop.buildings

        return (player_property_number, mean_op_property, num_color_completed, house_build, player_money, mean_op_money)

    def get_reward_parameters_from_regular(self, state: MSs.RegularMonopolyState):
        player_property_number = 0
        mean_op_property = 0
        num_color_completed = 0
        house_build = 0
        player_money = 0
        mean_op_money = 0

        oponents_money = []
        oponents_prop_num = []

        for pl in state.playersInGame:
            if pl.player_id == self.id_in_game:
                player_property_number = len(pl.properties)
                num_color_completed = pl.sets_completed
                player_money = pl.money

                for plprop in pl.properties:
                    if plprop.type == "street":
                        house_build += plprop.buildings
            else:
                oponents_money.append(pl.money)
                oponents_prop_num.append(len(pl.properties))

        if len(oponents_money) > 0:
            mean_op_property = sum(oponents_prop_num) / len(oponents_prop_num)
            mean_op_money = sum(oponents_money) / len(oponents_money)

        return (player_property_number, mean_op_property, num_color_completed, house_build, player_money, mean_op_money)

    # To calculate an actions reward
    def reward_function(self, player_property_number: int, mean_op_property: int, num_color_completed: int, 
        house_build: int, player_money: int, mean_op_money: int):

        self.reward_count += 1

        if num_color_completed >= 1:
            asset_factor = (player_property_number - mean_op_property) + (house_build / (5 * num_color_completed))
        else:
            asset_factor = player_property_number - mean_op_property

        finance_factor = player_money - mean_op_money

        xvalue = asset_factor + finance_factor
        res: float = xvalue / (1 + abs(xvalue))

        return res

    def calculate_fitness(self):
        return self.rewards_in_game / self.reward_count

    def reset_base_values(self):
        self.id_in_game = -1
        self.rewards_in_game = 0
        self.reward_count = 0
        self.last_action_initialization = None