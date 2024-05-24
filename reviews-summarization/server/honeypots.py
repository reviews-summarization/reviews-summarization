import random
import database
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

  def get_honeypot_reviews(self):
    honeypot_reviews = []
    for review in range(1, len(self.table)):
      honeypot_reviews.append(self.table[review][0])
    return honeypot_reviews

  def right_answer(self, review, aspect):
    for i in range(1, len(self.table)):
      if review != self.table[i][0]:
        continue
      for j in range(1, len(self.table[0])):
        if aspect == self.table[0][j]:
          return int(self.table[i][j])

    return None


def check_user():
  bad_users = {}

  honeypots = Honeypots()
  db = database.make_database()

  honeypot_reviews = honeypots.get_honeypot_reviews()
  for (review, aspect, answer, ip, session) in db.list_query(f'SELECT * FROM answers;'):
    if review in honeypot_reviews:
      wrong_all_honepots = bad_users.get(session, [0, 0])
      wrong_all_honepots[1] += 1
      ans = honeypots.right_answer(review, aspect)
      if answer != ans and ans != None:
        wrong_all_honepots[0] += 1
      bad_users[session] = wrong_all_honepots

  return bad_users


if __name__ == '__main__':
  print(check_user(), len(check_user()))
