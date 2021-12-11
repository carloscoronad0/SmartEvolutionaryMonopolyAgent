class RLTraining:
    def train_population(self, population, batch_percentage):
        for agent in population:
            if agent.agent_type == "street":
                agent.train(batch_percentage)