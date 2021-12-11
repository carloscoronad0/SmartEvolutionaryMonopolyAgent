import numpy as np
import pyfastrand as fastrand
from Network.DDQNActor import DdqnActor

PARAMETER_MUTATION_SEED = 0.1
RANDOM_SEED = 123

HYPPARAM_MUTATION = ["learning_rate", "gamma", "tau", "epsilon", "batch"]

MAX_LEARNING_RATE = 0.05
MIN_LEARNING_RATE = 0.001
LEARNING_RATE_STEP = 0.001

MAX_GAMMA = 0.99
MIN_GAMMA = 0.09
GAMMA_STEP = 0.01

MAX_TAU = 0.09
MIN_TAU = 0.001
TAU_STEP = 0.001

MAX_EPSILON = 0.9
MIN_EPSILON = 0.1
EPSILON_STEP = 0.1

MAX_BATCH_SIZE = 512
MIN_BATCH_SIZE = 16
BATCH_STEP = 8

class Mutation:
    def __init__(self):
        self.rng = np.random.RandomState()
    
    # NO MUTATION ------------------------------------------------------------------------
    def no_mutation(self, actor: DdqnActor) -> DdqnActor:
        print("No mutation")
        return actor
    # ------------------------------------------------------------------------------------

    # PARAMETER MUTATION -----------------------------------------------------------------
    def weight_mutation(self, actor: DdqnActor) -> DdqnActor:
        network = actor.regular_net
        mut_strength = PARAMETER_MUTATION_SEED
        num_mutation_frac = 0.1
        super_mut_strength = 10
        super_mut_prob = 0.05
        reset_prob = super_mut_prob + 0.05

        model_params = network.state_dict()

        potential_keys = []
        for i, key in enumerate(model_params):  # Mutate each param
            if not 'norm' in key:
                W = model_params[key]
                if len(W.shape) == 2:  # Weights, no bias
                    potential_keys.append(key)

        how_many = np.random.randint(1, len(potential_keys) + 1, 1)[0]
        chosen_keys = np.random.choice(potential_keys, how_many, replace=False)

        for key in chosen_keys:
            # References to the variable keys
            W = model_params[key]
            num_weights = W.shape[0] * W.shape[1]
            # Number of mutation instances
            num_mutations = fastrand.pcg32bounded(int(np.ceil(num_mutation_frac * num_weights)))
            for _ in range(num_mutations):
                ind_dim1 = fastrand.pcg32bounded(W.shape[0])
                ind_dim2 = fastrand.pcg32bounded(W.shape[-1])
                random_num = self.rng.uniform(0, 1)

                if random_num < super_mut_prob:  # Super Mutation probability
                    W[ind_dim1, ind_dim2] += self.rng.normal(0, np.abs(super_mut_strength * W[ind_dim1, ind_dim2]))
                elif random_num < reset_prob:  # Reset probability
                    W[ind_dim1, ind_dim2] = self.rng.normal(0, 1)
                else:  # mutauion even normal
                    W[ind_dim1, ind_dim2] += self.rng.normal(0, np.abs(mut_strength * W[ind_dim1, ind_dim2]))

                # Regularization hard limit
                W[ind_dim1, ind_dim2] = self.regularize_weight(W[ind_dim1, ind_dim2], 1000000)

        print("Weight mutation")
        
        return actor

    def regularize_weight(self, weight, mag):
        if weight > mag: weight = mag
        if weight < -mag: weight = -mag
        return weight

    # ------------------------------------------------------------------------------------

    # ACTIVATION FUNCTION MUTATION -------------------------------------------------------
    def activation_mutation(self, actor: DdqnActor) -> DdqnActor:
        actor.regular_net = self._permutate_activation(actor.regular_net)
        actor.target_net = self._permutate_activation(actor.target_net)

        print("Activation mutation")

        return actor

    def _permutate_activation(self, network):

        possible_activations = ['relu', 'elu', 'tanh']
        current_activation = network.activation
        possible_activations.remove(current_activation)
        new_activation = self.rng.choice(possible_activations, size=1)[0]
        net_dict = network.init_dict
        net_dict['activation'] = new_activation
        new_network = type(network)(**net_dict)
        new_network.load_state_dict(network.state_dict())
        network = new_network

        return network

    # ------------------------------------------------------------------------------------

    # ARCHITECTURE MUTATION --------------------------------------------------------------
    def architecture_mutate(self, actor: DdqnActor):

        offspring_regular = actor.regular_net.clone()
        offspring_target = actor.target_net.clone()

        rand_numb = self.rng.uniform(0, 1)
        if rand_numb < 0.5:
            offspring_regular.add_layer()
            offspring_target.add_layer()

            print("New layer mutation")

        else:
            node_dict = offspring_regular.add_node()
            offspring_target.add_node(**node_dict)

            print("New node mutation")

        actor.regular_net = offspring_regular
        actor.target_net = offspring_target

        return actor

    # ------------------------------------------------------------------------------------

    # HYPER-PARAMETER MUTATION -----------------------------------------------------------
    def rl_hyperparam_mutation(self, actor: DdqnActor) -> DdqnActor:

        mutate_param = self.rng.choice(HYPPARAM_MUTATION, 1)[0]

        if mutate_param == "learning_rate":
            self.mutate_hypp(actor.learning_rate, MAX_LEARNING_RATE, MIN_LEARNING_RATE, LEARNING_RATE_STEP)
        elif mutate_param == "gamma":
            self.mutate_hypp(actor.gamma, MAX_GAMMA, MIN_GAMMA, GAMMA_STEP)
        elif mutate_param == "tau":
            self.mutate_hypp(actor.tau, MAX_TAU, MIN_TAU, TAU_STEP)
        elif mutate_param == "epsilon":
            self.mutate_hypp(actor.epsilon, MAX_EPSILON, MIN_EPSILON, EPSILON_STEP)

        print(f"{mutate_param} mutation")

        return actor

    def mutate_hypp(self, parameter: int, max_value: int, min_value: int, step: int):
        random_num = self.rng.uniform(0, 1)
        if random_num < 0.5:
            if parameter > min_value:
                parameter -= step
        else:
            if parameter < max_value:
                parameter += step