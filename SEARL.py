from Monopoly.models.AgentModels.SmartAgentModel import SmartAgent
from Monopoly.models.AgentModels.FixedAgentModel import FixedAgent
from Network.ReplayMemory import BasicBuffer
from SearlFramework.Tournament import TournamentSelection
from SearlFramework.EvaluationInEnv import Evaluation
from SearlFramework.PopulationMutation import PopMutation
from SearlFramework.TrainingPopulation import RLTraining

import random
import numpy as np

GENERATION_NUMBER = 4
TRAINING_FRACTION = 0.25
POPULATION_SIZE = 12

SMART_AGENTS_AMOUNT = 10
FIXED_AGENTS_AMOUNT = 2

FIXED_PRIORITIZE = [["railroad", "orange"], ["lightblue", "red"]]
FIXED_AVOID = [["utility"], []]

#region INITIALIZATION

regular_buffer = BasicBuffer(100000)
trade_buffer = BasicBuffer(100000)

evaluation = Evaluation()
tournament = TournamentSelection()
mutation = PopMutation()
training = RLTraining()

agent_population = []

identifier = 0
for i in range(0, SMART_AGENTS_AMOUNT):
    agent_population.append(SmartAgent(identifier, regular_buffer, trade_buffer))
    identifier += 1


for i in range(0, FIXED_AGENTS_AMOUNT):
    agent_population.append(FixedAgent(identifier, FIXED_PRIORITIZE[i], FIXED_AVOID[i]))
    identifier += 1

#endregion INITIALIZATION

for g in range(GENERATION_NUMBER):

    #region EVALUATION

    fitness_list = evaluation.evaluation(agent_population, 4)
    print(fitness_list)

    #endregion EVALUATION

    #region TOURNAMENT_SELECTION

    elite, new_population = tournament.select(agent_population, fitness_list, POPULATION_SIZE)
    print("\n ------------- New population ------------- \n")
    print([(ag.agent_id, ag.agent_type) for ag in new_population])
    print(elite.agent_id)

    #endregion TOURNAMENT_SELECTION

    #region MUTATION

    agent_population = mutation.mutate_population(new_population)

    #endregion MUTATION

    #region TRAINING

    training.train_population(agent_population, TRAINING_FRACTION)

    #endregion TRAINING