import os
import json
import uuid
from pathlib import Path

import mysql.connector

ASPECTS = [
  'Режиссерская работа',
  'Саундтрек/музыка',
  'Актерская игра',
  'Визуальные эффекты',
  'Эмоциональное воздействие',
  'Раскрытие темы',
  'Оригинальность сюжета',
  'Юмор',
  'Дизайн постановки/костюмов',
]


def load_reviews(cnx):
  data = json.loads(Path('data.json').read_text())
  cursor = cnx.cursor()
  new_data = []
  for k, v in data.items():
    for x in v["reviews"][:min(len(v), 100)]:
      new_data.append((int(k), v["name"], x, str(uuid.uuid4())))
  for x in new_data:
    cursor.execute(
      "INSERT INTO reviews (film_id, film_name, review_body, id) VALUES (%s, %s, %s, %s)",
      x
    )
  cnx.commit()
  cursor.close()


def load_aspects(cnx):
  new_data = [(str(uuid.uuid4()), x) for x in ASPECTS]
  cursor = cnx.cursor()
  for x in new_data:
    cursor.execute(
      "INSERT INTO aspects (id, aspect) VALUES (%s, %s)", x
    )
  cnx.commit()
  cursor.close()


def main():
  cnx = mysql.connector.connect(
    user=os.environ.get('DB_USER'),
    database=os.environ.get('DB_NAME'),
    passwd=os.environ.get('DB_PASSW')
  )
  load_aspects(cnx)
  load_reviews(cnx)
  cnx.close()


if __name__ == '__main__': main()
