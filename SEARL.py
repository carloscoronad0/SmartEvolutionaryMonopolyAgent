from Monopoly.models.AgentModels.SmartAgentModel import SmartAgent
from Monopoly.models.AgentModels.FixedAgentModel import FixedAgent
from Network.ReplayMemory import BasicBuffer
from SearlFramework.Tournament import TournamentSelection
from SearlFramework.EvaluationInEnv import Evaluation
from SearlFramework.PopulationMutation import PopMutation
from SearlFramework.TrainingPopulation import RLTraining

import Data.Game_Logger as gl
import random

GENERATION_NUMBER = 20
TRAINING_FRACTION = 0.25
POPULATION_SIZE = 12
EXPERIMENTS_NUMBER = 100

SMART_AGENTS_AMOUNT = 10
FIXED_AGENTS_AMOUNT = 2

FIXED_PRIORITIZE = [["railroad", "darkblue"], ["lightblue", "orange"]]
FIXED_AVOID = [["utility"], ["utility"]]

#region INITIALIZATION

regular_buffer = BasicBuffer(2000000)
trade_buffer = BasicBuffer(2000000)

eval_log = gl.setup_logger("Evaluation", "Data/SEARL")
print("Creating Evaluation logger")
tourn_log = gl.setup_logger("Tournamet", "Data/SEARL")
print("Creating Tournament logger")
mut_log = gl.setup_logger("Mutation", "Data/SEARL")
print("Creating Mutation logger")
train_log = gl.setup_logger("Train", "Data/SEARL")
print("Creating Train logger")

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
print("\n---------------- Starting SEARL ----------------")
for gen in range(0, GENERATION_NUMBER):

    print(f"\nGeneration {gen} -------------\n")

    population_log = gl.setup_logger(f"Population_{gen}", "Data/Populations")
    #region EVALUATION
    for ag in agent_population:
        if ag.agent_type == "smart":
            population_log.info(f"{ag.agent_id};{ag.agent_type};{ag.regular_actor.info()};{ag.trading_actor.info()}")
        elif ag.agent_type == "fixed":
            population_log.info(f"{ag.agent_id};{ag.agent_type};{ag.prioritize};{ag.avoid}")

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

print("Saving final population information")
final_agents_log = gl.setup_logger("Final_Population","Data/Populations")
for ag in agent_population:
    if ag.agent_type == "smart":
        final_agents_log.info(f"{ag.agent_id};{ag.agent_type};{ag.regular_actor.info()};{ag.trading_actor.info()}")
    elif ag.agent_type == "fixed":
        final_agents_log.info(f"{ag.agent_id};{ag.agent_type};{ag.prioritize};{ag.avoid}")

print("---------------- Finishing SEARL ----------------\n")

#region EXPERIMENTS

print("------------- Starting Experiments --------------")

print("Getting the elite agent from the last generation")
fitness_list = evaluation.evaluation(agent_population, 4, f"searl_{GENERATION_NUMBER}")
elite, new_population = tournament.select(agent_population, fitness_list, POPULATION_SIZE)

# EXPERIMENTS --------------------------------

print("Creating experiment population")
experiment_population = []
experiment_population.append(elite)
experiment_population.append(new_population[random.randint(0, (len(new_population) - 1))])

for i in range(0, FIXED_AGENTS_AMOUNT):
    experiment_population.append(FixedAgent(i, FIXED_PRIORITIZE[i], FIXED_AVOID[i]))

print("Saving experiment population info")
exp_agents_log = gl.setup_logger("Experiment_Population","Data/Experiments")
for ag in experiment_population:
    if ag.agent_type == "smart":
        exp_agents_log.info(f"{ag.agent_id};{ag.agent_type};{ag.regular_actor.info()};{ag.trading_actor.info()}")
    elif ag.agent_type == "fixed":
        exp_agents_log.info(f"{ag.agent_id};{ag.agent_type};{ag.prioritize};{ag.avoid}")

print("Creating general logs for experiments")
fitness_log = gl.setup_logger("Fitness", "Data/Experiments")
exp_eval_log = gl.setup_logger("Evaluation", "Data/Experiments")
exp_evaluation = Evaluation(exp_eval_log)

print("Running experiments")
for exp in range(0, EXPERIMENTS_NUMBER):
    exp_gen = f"exp_{exp}"
    fitness_list = exp_evaluation.evaluation(experiment_population, 4, exp_gen)
    fitness_log.info(f"{exp_gen};{fitness_list}")

print("------------- Finishing Experiments --------------")
#endregion EXPERIMENTS