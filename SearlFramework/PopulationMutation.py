from Network.NetworkMutation import Mutation
import random

MUTATION_NUMBER = 4

class PopMutation:
    def __init__(self, mut_log) -> None:
        self.mutation = Mutation()
        self.mut_log = mut_log

    def mutate_population(self, population):
        for ag in population:
            if ag.agent_type == "smart":
                mut = random.randint(0, MUTATION_NUMBER)
                if mut == 0:
                    ag.regular_actor = self.mutation.weight_mutation(ag.regular_actor)
                    ag.trading_actor = self.mutation.weight_mutation(ag.trading_actor)
                    self.mut_log.info(f"{ag.agent_id};Weight Mutation")
                    print(f"Mutating Weights agent {ag.agent_id}")
                elif mut == 1:
                    ag.regular_actor = self.mutation.activation_mutation(ag.regular_actor)
                    ag.trading_actor = self.mutation.activation_mutation(ag.trading_actor)
                    self.mut_log.info(f"{ag.agent_id};Activation Mutation")
                    print(f"Mutating Activation agent {ag.agent_id}")
                elif mut == 2:
                    ag.regular_actor = self.mutation.architecture_mutate(ag.regular_actor)
                    ag.trading_actor = self.mutation.architecture_mutate(ag.trading_actor)
                    self.mut_log.info(f"{ag.agent_id};Architecture Mutation")
                    print(f"Mutating Architecture agent {ag.agent_id}")
                elif mut == 3:
                    ag.regular_actor = self.mutation.rl_hyperparam_mutation(ag.regular_actor)
                    ag.trading_actor = self.mutation.rl_hyperparam_mutation(ag.trading_actor)
                    self.mut_log.info(f"{ag.agent_id};Hyper Parameter Mutation")
                    print(f"Mutating Hyper Parameters agent {ag.agent_id}")
                elif mut == 4:
                    ag.regular_actor = self.mutation.no_mutation(ag.regular_actor)
                    ag.trading_actor = self.mutation.no_mutation(ag.trading_actor)
                    self.mut_log.info(f"{ag.agent_id};No Mutation")
                    print(f"No Mutation agent {ag.agent_id}")

        return population