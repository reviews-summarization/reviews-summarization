import os
import random
import json

import database
import honeypots

import requests


FILM_PROMPT = """
Ответь присутствует ли аспект "{aspect}" в следующем отзыве на фильм:
"""
SYSTEM_PROMPT = """
Ты кинокритик, твоя задача отвечать на вопросы присутствует ли аспект "{review}"
в отзыве на фильм. У тебя есть следующие варианты ответа: "Хвалят", "Ругают", 
"Отсутствует", твой ответ должен иметь только одно слово
"""


def ask_gpt4(aspect, review):
  prompt = SYSTEM_PROMPT + FILM_PROMPT
  print(prompt.format(aspect=aspect, review=review))
  r = requests.post(
      url='http://soyproxy.yandex-team.ru/proxy/openai/v1/chat/completions',
      data=json.dumps({
        "model": "gpt-4-turbo",
        "messages": [{
            "role": "user",
            "content": prompt.format(aspect=aspect, review=review)
        }]
      }, ensure_ascii=False).encode('utf-8'),
      headers={
        "Authorization": f"OAuth {os.environ.get('SOYPROXY_TOKEN')}"
      },
      timeout=300,
  )
  return r.json()['response']['choices'][0]['message']['content'] \
    if r.status_code == 200 else None


def ask_alice(aspect, review):
  print((SYSTEM_PROMPT + FILM_PROMPT).format(aspect=aspect, review=review))
  r = requests.post(
    url='https://llm.api.cloud.yandex.net/foundationModels/v1/completion',
    data=json.dumps({
      "modelUri": "gpt://b1gnvamp52fkd3o27c7m/yandexgpt/latest",
      "completionOptions": {
        "temperature": 0.1,
        "stream": False,
        "maxTokens": "2000"
      },
      "messages": [
        {"role": "system", "text": SYSTEM_PROMPT.format(review=review)},
        {"role": "user", "text": FILM_PROMPT.format(aspect=aspect),}
      ]
    }, ensure_ascii=False).encode('utf-8'),
    headers={
      "Authorization": f"Bearer {os.environ.get('YC_CLOUD_TOKEN')}"
    },
    timeout=300
  )
  print(r.json())
  return r.json()['result']['alternatives'][0]['message']['text'] \
    if r.status_code == 200 else None


def get_random(db):
  (aspect_id, aspect_body) = db.get_random('aspects')
  if random.random() < 0.1:
    (review_id, _) = honeypots.Honeypots().get_random()
    (_, _, text_body, review_id) = db.get('reviews', review_id)
  else:
    if random.random() < 0.5:  # balancing good and bad films
      (_, _, text_body, review_id) = db.get_random('reviews')
    else:
      (_, _, _, text_body, review_id) = db.list_query('''
        SELECT * FROM (
          SELECT @rownum:=@rownum+1 AS rownum, t.*
          FROM (SELECT @rownum:=0) r, reviews t
        ) x
        WHERE x.rownum BETWEEN 18001 AND 21770 ORDER BY RAND() LIMIT 1;
        '''
      )[0]
  return ((review_id, text_body), (aspect_id, aspect_body))


def main():
  db = database.make_database()
  for _ in range(2000):
    ((review_id, text_body), (aspect_id, aspect_body)) = get_random(db)
    # answer = ask_gpt4(aspect_body, text_body).strip()
    answer = ask_alice(aspect_body, text_body)
    print(answer)
    if not answer: continue
    answer = answer.strip()
    answers = {'Хвалят': 1, 'Ругают': 0, 'Отсутствует': 2}
    if answer not in answers: continue
    print('Recording')
    db.add_record(
      'answers',
      (review_id, aspect_id, answers[answer], '0.0.0.0', 'alice')
    )
    print('-'* 10)


if __name__ == '__main__': main()
