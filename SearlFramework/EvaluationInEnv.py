import random
import Data.Game_Logger as gl

from Monopoly.MonopolyGame import MonopolyGame

class Evaluation:
    def __init__(self, eval_log):
        self.eval_log = eval_log
        
    def divide_chunks(self, l, n):
        for i in range(0, len(l), n): 
            yield l[i:i + n]

    def evaluation(self, agent_population, player_per_game_division, generation):
        fitness_list = [0 for _ in range(len(agent_population))]

        order = [n for n in range(len(agent_population))]
        random.shuffle(order)
        player_division = list(self.divide_chunks(order, player_per_game_division))

        evaluation_game_number = len(player_division)

        for game in range(0, evaluation_game_number):
            agents = [agent_population[a] for a in player_division[game]]
            action_log = gl.setup_logger(f"Gen_{generation}_Game_{game}_Agents_{agents}", "Data/Actions")
            trade_log = gl.setup_logger(f"Gen_{generation}_Game_{game}_Agents_{agents}", "Data/Trades")
            print(f"\nSTARTING GAME {game} \n")
            eval_game = MonopolyGame(agents, action_log, trade_log)
            winner = eval_game.monopoly_game()
            print(f"\n WINNER GAME {game} : {winner.agent.agent_id}\n")
            
            temp_fitness = []
            for a in player_division[game]:
                fitness_value = agent_population[a].calculate_fitness()

                fitness_list[a] = fitness_value
                temp_fitness.append(fitness_value)

            self.eval_log.info(f"{generation};{game};{winner.agent.agent_id};{winner.agent.agent_type};{agents};{temp_fitness}")

        return fitness_list