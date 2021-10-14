from abc import ABC, abstractmethod


class Agent(ABC):
    @abstractmethod
    def take_decisions(self):
        pass