from Network.EvolvableNeuralNetwork import EvolvableNN

import torch
import torch.nn.functional as F
import numpy as np
import random

STARTING_HIDDEN_SIZE = [64, 64]
STARTING_HIDDEN_ACTIVATION = ['relu', 'relu']

PERCENTAJE_TO_SAVE = 0.5

class DdqnActor:
    def __init__(self, state_size: int, decision_size: int, learning_rate: float, 
                gamma: float, tau: float, epsilon: float, memory_replay, distinguisher: str,
                batch_size: int):
        self.net = EvolvableNN()

        self.learning_rate = learning_rate
        self.gamma = gamma
        self.tau = tau
        self.epsilon = epsilon
        
        self.batch_size = batch_size
        self.memory_replay = memory_replay

        self.done = False

        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        self.regular_net = EvolvableNN(state_size, decision_size, STARTING_HIDDEN_SIZE, 
                                        STARTING_HIDDEN_ACTIVATION, 'sigmoid').to(self.device)

        self.target_net = EvolvableNN(state_size, decision_size, STARTING_HIDDEN_SIZE, 
                                        STARTING_HIDDEN_ACTIVATION, 'sigmoid').to(self.device)

        for target_param, param in zip(self.model.parameters(), self.target_model.parameters()):
            target_param.data.copy_(param)

        self.optimizer = torch.optim.Adam(self.regular_net.parameters())

        self.distinguisher = distinguisher

    def get_action(self, state: np.ndarray) -> np.ndarray:
        state = torch.FloatTensor(state)
        qvals = self.regular_net.forward(state)
        decisions = qvals.cpu().detach().numpy()

        if random.uniform(0,1) < self.epsilon:
            decisions = np.array([round(random.uniform(0,1)) for _ in range(state.shape[0])])

        if random.uniform(0,1) > 0.5:
            # Save decision in memory replay
            pass

        return decisions

    def compute_loss(self, state, action, reward, next_state):
        state = torch.FloatTensor(state)
        action = torch.FloatTensor(action)
        reward = torch.FloatTensor(reward)
        next_state = torch.FloatTensor(next_state)

        curr_Q = self.regular_net.forward(state)
        next_Q = self.target_net.forward(next_state)

        expected_Q = reward + (self.gamma * next_Q)
        loss = F.mse_loss(curr_Q, expected_Q.detach())
        
        return loss

    def train(self):
        batch = self.memory_replay.sample(self.batch_size)
        self.optimizer.zero_grad()

        for experience in batch:
            state, action, reward, next_state = experience
            self.optimizer.zero_grad()
            loss = self.compute_loss(state, action, reward, next_state)
            loss.backward()
            self.optimizer.step()
        
        # target network update
        for target_param, param in zip(self.target_net.parameters(), self.regular_net.parameters()):
            target_param.data.copy_(self.tau * param + (1 - self.tau) * target_param)