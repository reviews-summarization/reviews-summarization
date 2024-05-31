import random
import sys
import secrets
import logging
from pathlib import Path


sys.path.append(str(Path(__file__).parents[1] / 'data'))
import database
import honeypots

import waitress
from flask import Flask, render_template, redirect, request, session


ASPECT_STATES = {'good': 1, 'bad': 0, 'absence': 2, 'skip': 3}
ASPECT_TEMPLATE = """
<div style="display: flex; justify-content: space-between; align-items: center;">
  <div style="flex-grow: 1;">
    <p style="text-align: left;">{name}</p>
  </div>
  <div style="flex-grow: 0;text-align: right;">
    <select name="{aspect_id}">
      <option value="good">Хорошо</option>
      <option value="bad">Плохо</option>
      <option value="absence">Отсутствует</option>
      <option value="skip" selected="">Пропустить</option>
    </select>
  </div>
</div>
"""

app = Flask(__name__)
app.secret_key = secrets.token_hex()
db = database.make_database()


@app.route('/submit', methods=['POST', 'GET'])
def submit():
  for aspect_id, _ in db.all('aspects'):
    aspect_state = request.form.get(aspect_id)
    if aspect_state == 'skip': continue
    _record_action(aspect_id, ASPECT_STATES[aspect_state])
  return redirect('/')


@app.route('/skip', methods=['POST'])
def skip():
  return redirect('/')


def _make_aspects():
  return '\n'.join([
    ASPECT_TEMPLATE.format(name=name, aspect_id=aspect_id)
    for aspect_id, name in db.all('aspects')
  ])


@app.route('/')
def index():
  if 'session_id' not in session:
    session['session_id'] = secrets.token_hex()
  if random.random() < 0.2:
    (review_id, _) = honeypots.Honeypots().get_random()
    (_, film_name, text_body, review_id) = db.get('reviews', review_id)
  else:
    (_, film_name, text_body, review_id) = db.get_random('reviews')
  session.update({'review_id': review_id})
  return render_template(
    "index.html",
    film_name=film_name,
    review=text_body,
    aspects=_make_aspects()
  )


def _record_action(aspect_id, number):
  db.add_record('answers', (
    session['review_id'],
    aspect_id,
    number,
    request.environ.get('REMOTE_ADDR', request.remote_addr),
    session['session_id']
  ))


def main():
  logger = logging.getLogger('waitress')
  logger.setLevel(logging.DEBUG)
  waitress.serve(app, host="0.0.0.0", port=8001)


if __name__ == "__main__": main()
