import random
from collections import deque

class BasicBuffer:

  def __init__(self, max_size):
      self.max_size = max_size
      self.buffer = deque(maxlen=max_size)
      self.push_count = 0

  def push(self, state, action, reward, next_state):
      experience = (state, action, reward, next_state)
      self.buffer.append(experience)
      self.push_count += 1

  def sample(self, batch_size):
      batch = random.sample(self.buffer, batch_size)
      return batch

  def __len__(self):
      return len(self.buffer)