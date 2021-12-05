from abc import ABC, abstractmethod


class Agent(ABC):
    def __init__(self, agent_id: int, fitness: int, agent_type: str):
        self.agent_id = agent_id
        self.fitness = fitness
        self.agent_type = agent_type

    @abstractmethod
    def take_decisions(self, valid_actions, state):
        pass
    
    @abstractmethod
    def decision_quality(self, resulting_state, decisions_to_inform, args_list):
        pass
