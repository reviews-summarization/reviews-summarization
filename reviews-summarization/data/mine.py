import os
import sys
import json
from pathlib import Path

#pylint: disable=wrong-import-position
PATH = (Path(__file__).parents[1] / 'server').resolve()
sys.path.insert(0, str(PATH))
import database

import requests
#pylint: enable=wrong-import-position


PROMPT = """
Ты кинокритик, твоя задача отвечать на вопросы присутствует тот или иной аспект
в отзыве на фильм. У тебя есть следующие варианты ответа: "Хвалят", "Ругают",
"Отсутствует", твой ответ должен иметь только одно слово

Ответь присутствует ли аспект "{aspect}" в следующем отзыве на фильм:

{review}
"""


def ask_gpt4(aspect, review):
  print(PROMPT.format(aspect=aspect, review=review))
  r = requests.post(
      url='http://soyproxy.yandex-team.ru/proxy/openai/v1/chat/completions',
      data=json.dumps({
        "model": "gpt-4-turbo",
        "messages": [{
            "role": "user",
            "content": PROMPT.format(aspect=aspect, review=review)
        }]
      }, ensure_ascii=False).encode('utf-8'),
      headers={
        "Authorization": \
          f"OAuth {os.environ.get('SOYPROXY_TOKEN')}"
      },
      timeout=300,
  )
  return r.json()['response']['choices'][0]['message']['content'] \
    if r.status_code == 200 \
    else None


def ask_alice(aspect, review):
  print(PROMPT.format(aspect=aspect, review=review))
  r = requests.post(
    url='https://llm.api.cloud.yandex.net/foundationModels/v1/completion',
    data=json.dumps({
      "modelUri": "gpt://b1gnvamp52fkd3o27c7m/yandexgpt/latest",
      "completionOptions": {
        "temperature": 0.1,
        "stream": False,
        "maxTokens": "2000"
      },
      "messages": [{
          "role": "user",
          "text": PROMPT.format(aspect=aspect, review=review),
      }]
    }, ensure_ascii=False).encode('utf-8'),
    headers={
      "Authorization": \
          f"Bearer {os.environ.get('YC_CLOUD_TOKEN')}"
    },
    timeout=300
  )
  return r.json()['result']['alternatives'][0]['message']['text'] \
    if r.status_code == 200 \
    else None


def get_random(db):
  (_, _, text_body, review_id) = db.get_random('reviews')
  (aspect_id, aspect_body) = db.get_random('aspects')
  return ((review_id, text_body), (aspect_id, aspect_body))


def main():
  db = database.make_database()
  for _ in range(10):
    ((review_id, text_body), (aspect_id, aspect_body)) = get_random(db)
    # answer = ask_gpt4(aspect_body, text_body).strip()
    answer = ask_alice(aspect_body, text_body)
    if not answer: continue
    answer = answer.strip()
    print(answer)
    answers = {
      'Хвалят': 1,
      'Ругают': 0,
      'Отсутствует': 2
    }
    if answer not in answers: continue
    db.add_record((
      review_id,
      aspect_id,
      answers[answer],
      '0.0.0.0',
      'alice'
    ))
    print('-'* 10)


if __name__ == '__main__': main()
