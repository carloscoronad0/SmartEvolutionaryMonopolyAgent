from abc import ABC, abstractmethod


class Agent(ABC):
    @abstractmethod
    def take_decisions(self, valid_actions, state):
        pass

    def decision_quality(self, decisions_to_inform, args_list):
        pass