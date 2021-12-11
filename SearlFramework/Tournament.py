import copy
import numpy as np


class TournamentSelection:

    def _tournament(self, ranks, tournament_size):
        selection = np.random.randint(0, len(ranks), size=tournament_size)
        selection_values = [ranks[i] for i in selection]
        winner = selection[np.argmax(selection_values)]
        return winner

    def select(self, population, fitness_values, population_size):
        rank = np.argsort(fitness_values).argsort()

        max_id = max([ag.agent_id for ag in population])

        elite = copy.deepcopy([population[np.argsort(rank)[-1]]][0])

        new_population = []
        new_population.append(elite.clone(elite.agent_id))
        selection_size = population_size - 1

        for _ in range(selection_size):
            max_id += 1
            agent_parent = population[self._tournament(rank, 3)]
            new_individual = agent_parent.clone(max_id)
            new_population.append(new_individual)

        return elite, new_population