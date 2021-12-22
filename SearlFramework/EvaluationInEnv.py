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
        print("\nCONFIGURING EVALUATION ENVIRONMENT")
        fitness_list = [0 for _ in range(len(agent_population))]

        print("Dividing agents")
        order = [n for n in range(len(agent_population))]
        random.shuffle(order)
        player_division = list(self.divide_chunks(order, player_per_game_division))

        evaluation_game_number = len(player_division)

        for game in range(0, evaluation_game_number):
            print(f"CONFIGURING GAME {game} EVALUATION")

            action_log = gl.setup_logger(f"Gen_{generation}_Game_{game}_Actions", "Data/Actions")
            print(f"\tAction logger Gen_{generation}_Game_{game}_Actions.log LOADED")

            trade_log = gl.setup_logger(f"Gen_{generation}_Game_{game}_Trade", "Data/Trades")
            print(f"\tTrade logger Gen_{generation}_Game_{game}_Trade.log LOADED")

            agents = [agent_population[a] for a in player_division[game]]
            evaluation_info = [(ag.agent_id, ag.agent_type) for ag in agents]
            print(f"\tPlayers to take part in game {game} : {evaluation_info}")

            print(f"STARTING GAME {game}")
            eval_game = MonopolyGame(agents, action_log, trade_log)
            winner, method = eval_game.monopoly_game()
            print(f"WINNER GAME {game} : {winner.agent.agent_id} : {method}")
            
            temp_fitness = []
            for a in player_division[game]:
                fitness_value = agent_population[a].calculate_fitness()
                agent_population[a].reset_base_values()

                fitness_list[a] = fitness_value
                temp_fitness.append(fitness_value)

            print(f"Fitness values : {temp_fitness}")

            agents_id = [ag.agent_id for ag in agents]
            self.eval_log.info(f"{generation};{game};{method};{winner.agent.agent_id};{winner.agent.agent_type};{agents_id};{temp_fitness}")

        return fitness_list