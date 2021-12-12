from Monopoly.models.AgentModels.SmartAgentModel import SmartAgent
from Monopoly.models.AgentModels.FixedAgentModel import FixedAgent
from Network.ReplayMemory import BasicBuffer
from SearlFramework.Tournament import TournamentSelection
from SearlFramework.EvaluationInEnv import Evaluation
from SearlFramework.PopulationMutation import PopMutation
from SearlFramework.TrainingPopulation import RLTraining

import Data.Game_Logger as gl
import random
import numpy as np

GENERATION_NUMBER = 4
TRAINING_FRACTION = 0.25
POPULATION_SIZE = 12
EXPERIMENTS_NUMBER = 10

SMART_AGENTS_AMOUNT = 10
FIXED_AGENTS_AMOUNT = 2

FIXED_PRIORITIZE = [["railroad", "orange"], ["lightblue", "red"]]
FIXED_AVOID = [["utility"], []]

#region INITIALIZATION

regular_buffer = BasicBuffer(100000)
trade_buffer = BasicBuffer(100000)

eval_log = gl.setup_logger("Evaluation", "Data/SEARL")
tourn_log = gl.setup_logger("Tournamet", "Data/SEARL")
mut_log = gl.setup_logger("Mutation", "Data/SEARL")
train_log = gl.setup_logger("Train", "Data/SEARL")

evaluation = Evaluation(eval_log)
tournament = TournamentSelection(tourn_log)
mutation = PopMutation(mut_log)
training = RLTraining(train_log)

agent_population = []

identifier = 0
for i in range(0, SMART_AGENTS_AMOUNT):
    agent_population.append(SmartAgent(identifier, regular_buffer, trade_buffer))
    identifier += 1


for i in range(0, FIXED_AGENTS_AMOUNT):
    agent_population.append(FixedAgent(identifier, FIXED_PRIORITIZE[i], FIXED_AVOID[i]))
    identifier += 1

#endregion INITIALIZATION
print("---------------- Starting SEARL ----------------")
for gen in range(GENERATION_NUMBER):

    print(f"Generation {gen + 1} -------------")
    #region EVALUATION

    print("Evaluation -------------")
    searl_gen = f"searl_{gen}"
    fitness_list = evaluation.evaluation(agent_population, 4, searl_gen)

    #endregion EVALUATION

    #region TOURNAMENT_SELECTION

    print("Tournament -------------")
    elite, new_population = tournament.select(agent_population, fitness_list, POPULATION_SIZE)

    #endregion TOURNAMENT_SELECTION

    #region MUTATION

    print("Mutation ---------------")
    agent_population = mutation.mutate_population(new_population)

    #endregion MUTATION

    #region TRAINING

    print("Training ---------------")
    training.train_population(agent_population, TRAINING_FRACTION)

    #endregion TRAINING

#region EXPERIMENTS

final_agents_log = gl.setup_logger("Agents","Data/Experiments")
for ag in agent_population:
    final_agents_log.info(f"{ag.agent_id};{ag.agent_type}")

fitness_log = gl.setup_logger("Fitness", "Data/Experiments")
for exp in EXPERIMENTS_NUMBER:
    exp_log = gl.setup_logger(f"{exp}-Experiment", "Data/Experiments")
    exp_eval = Evaluation(exp_log)
    exp_gen = f"exp_{exp}"
    fitness_list = evaluation.evaluation(agent_population, 4, exp_gen)
    fitness_log.info(f"{exp_gen};{fitness_list}")

#endregion EXPERIMENTS