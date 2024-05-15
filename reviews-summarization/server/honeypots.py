import random
from pathlib import Path

class Honeypots:
  def __init__(
        self,
        csv:Path=(Path(__file__).parent / 'data/honeypots.csv').resolve()
      ):
    self.table = [line.split(';') for line in csv.read_text().split()]

  def get_random(self):
    review = random.randint(1, len(self.table) - 1)
    aspect = random.randint(1, len(self.table[0]) - 1)
    return (self.table[review][0], self.table[0][aspect])
