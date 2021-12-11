import random
from Monopoly.MonopolyGame import MonopolyGame


class Evaluation:

    def divide_chunks(self, l, n):
        for i in range(0, len(l), n): 
            yield l[i:i + n]

    def evaluation(self, agent_population, player_per_game_division):
        fitness_list = [0 for _ in range(len(agent_population))]

        order = [n for n in range(len(agent_population))]
        random.shuffle(order)
        player_division = list(self.divide_chunks(order, player_per_game_division))
        print(player_division)

        evaluation_game_number = len(player_division)

        for game in range(0, evaluation_game_number):
            agents = [agent_population[a] for a in player_division[game]]
            print(f"\n---------------------- STARTING GAME {game} ----------------------\n")
            eval_game = MonopolyGame(agents)
            winner = eval_game.monopoly_game()
            print(f"\n----------------------- WINNER GAME {game} -----------------------\n")
            print(winner.agent.agent_id)

            for a in player_division[game]:
                fitness_list[a] = agent_population[a].calculate_fitness()

        return fitness_list