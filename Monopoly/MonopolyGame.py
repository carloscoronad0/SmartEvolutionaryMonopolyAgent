from Monopoly.models.AgentModels.AgentModel import Agent
from Monopoly.models.MonopolyTableModel import MonopolyTable
from Monopoly.models.PlayerModel import Player
from typing import List, Tuple

import random

STARTING_MONEY = 1500

class MonopolyGame:
    def __init__(self, agents: List[Agent]):
        self.player_number = len(agents)

        self.dice = (0,0)
        self.table = MonopolyTable()
        self.players = [Player(id=i, money=STARTING_MONEY, agent=agents[i]) for i in range(0, self.player_number)]

    def roll_dice(self) -> Tuple[int, int]:
        return (random.randrange(1,6), random.randrange(1,6))

    def move_player(self, player: Player) -> int:
        new_position = player.advance(sum(self.dice))
        return new_position

    def go_to_jail(self, player: Player):
        pass

    def actions_available_for_player(self, player: Player):
        pass

    def step(self, player: Player):
        doubles = 0 # number of doubles in the player's turn
        continue_turn = True # continue rolling the dice

        while continue_turn:

            # PRE ROLL ACTIONS --------------------------------------------------------

            # Roll dice
            self.dice = self.roll_dice()

            # If the dice is double
            if self.dice[0] == self.dice[1]:
                doubles += 1 # The number adds up

                if doubles == 3: # If the number is already 3
                    self.go_to_jail(player) # The player goes to jail
                    continue_turn = False # The player's turn ends
            else:
                # If it's not a double, then the player has no right to throw again
                continue_turn = False

            # POST ROLL ACTIONS -------------------------------------------------------

            # Decide which actions the player can take

            # Recieving player actions
            player.actions()

            # Implementing player actions

            # OUT OF TURN ACTIONS -------------------------------------------------------

