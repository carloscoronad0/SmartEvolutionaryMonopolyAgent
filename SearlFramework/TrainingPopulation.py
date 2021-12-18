class RLTraining:
    def __init__(self, train_log):
        self.train_log = train_log

    def train_population(self, population, batch_percentage):
        for agent in population:
            if agent.agent_type == "smart":
                print(f"In agent: {agent.agent_id}")
                print("\tTraining Regular Net")
                agent.regular_actor.train(batch_percentage, self.train_log, agent.agent_id, agent.agent_type)
                print("\tTraining Trading Net")
                agent.trading_actor.train(batch_percentage, self.train_log, agent.agent_id, agent.agent_type)