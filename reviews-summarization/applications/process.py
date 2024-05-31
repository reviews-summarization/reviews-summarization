import sys
import json
from pathlib import Path

import pandas as pd
from catboost import CatBoostClassifier

CUR_DIR = Path(__file__).parent
sys.path.append(str((CUR_DIR.parent / 'data').resolve()))
import kinopoisk


def prepare_date(data, aspect):
  df = data.copy()
  df = df[df['aspect'] == aspect]
  df = df.drop(['aspect'], axis=1)
  return df

def predict_film(film_id):
  kp = kinopoisk.make_kinopoisk()
  reviews = kp._get_reviews(f'{film_id}', page_number=1)
  df = pd.DataFrame(columns=['review', 'aspect'])
  k = 0
  for review in reviews:
    for aspect in kinopoisk.ASPECTS:
      df.loc[k] = [review, aspect]
      k += 1

  positives = []
  negatives = []
  dbg = {}
  for aspect, translation in kinopoisk.ASPECTS.items():
    revs = prepare_date(df, aspect)
    model = CatBoostClassifier().load_model(
      fname=(CUR_DIR.parent / 'notebooks' / 'models' / f'{translation}_model')
    )
    res = [x for x in model.predict(revs)]
    good = res.count('хорошо')
    bad = res.count('плохо')
    absence = res.count('отсутствует')
    every = max(good + bad + absence, 1)
    good = int(good * 100 / every)
    bad = int(bad * 100 / every)
    absence = int(absence * 100 / every)
    if good > bad and good > 10: positives.append(f'{aspect}  ({good}/{bad}/{absence})')
    elif bad > good and bad > 10: negatives.append(f'{aspect}  ({good}/{bad}/{absence})')
    dbg[aspect] = [good, bad, absence]
    # result += ' '.join([
    #   f'{aspect}:', 'Хорошо', str(good) + '%', 
    #   'Плохо', str(bad) + '%', 'Отств', str(absence) + '%'
    # ]) + '\n'
  result = ''
  for aspect in positives:
    result += f'+ {aspect}\n'
  for aspect in negatives:
    result += f'- {aspect}\n'
  return result


def main():
  print(predict_film(sys.argv[1]))


if __name__ == '__main__': main()

