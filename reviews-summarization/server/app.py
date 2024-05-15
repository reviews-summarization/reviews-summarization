import random
import secrets
import logging

import databse
import honeypots

import waitress
from flask import Flask, render_template, redirect, request, url_for, session  # pylint: disable=unused-import

app = Flask(__name__)
app.secret_key = secrets.token_hex()
db = databse.make_database()


@app.route('/yes_clicked', methods=['POST'])
def yes_clicked():
  _record_action(1)
  return redirect('/')


@app.route('/no_clicked', methods=['POST'])
def no_clicked():
  _record_action(0)
  return redirect('/')


@app.route('/absence_clicked', methods=['POST'])
def absence_clicked():
  _record_action(2)
  return redirect('/')


@app.route('/skip', methods=['POST'])
def skip():
  return redirect('/')


@app.route('/')
def index():
  #TODO: Use for user identification
  if 'session_id' not in session:
    session['session_id'] = secrets.token_hex()
  if random.random() < 0.1:
    (review_id, aspect_id) = honeypots.Honeypots().get_random()
    (_, film_name, text_body, review_id) = db.get('reviews', review_id)
    (aspect_id, aspect_body) = db.get('aspects', aspect_id)
  else:
    (_, film_name, text_body, review_id) = db.get_random('reviews')
    (aspect_id, aspect_body) = db.get_random('aspects')
  session.update({'review_id': review_id, 'aspect_id': aspect_id})
  return render_template(
    "index.html",
    film_name=film_name,
    review=text_body,
    aspect=aspect_body
  )


def _record_action(number):
  db.add_record((
    session['review_id'],
    session['aspect_id'],
    number,
    request.environ.get('REMOTE_ADDR', request.remote_addr),
    session['session_id']
  ))


def main():
  logger = logging.getLogger('waitress')
  logger.setLevel(logging.DEBUG)
  waitress.serve(app, host="0.0.0.0", port=8001)


if __name__ == "__main__": main()
