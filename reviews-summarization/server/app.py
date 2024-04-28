import os
import secrets
import logging

import mysql.connector
import waitress
from flask import Flask, render_template, redirect, request, url_for, session  # pylint: disable=unused-import

app = Flask(__name__)
app.secret_key = secrets.token_hex()

class DatabaseConnection:
  def __init__(self, **kwargs) -> None:
    self.kwargs = kwargs

  def __enter__(self):
    self.cnx = mysql.connector.connect(**self.kwargs)
    return self.cnx

  def __exit__(self, *args, **kwargs):
    self.cnx.close()


class Database:
  def __init__(self, **db_config):
    self.db_config = db_config

  def query(self, *args, **kwargs):
    with DatabaseConnection(**self.db_config) as cnx:
      cursor = cnx.cursor()
      cursor.execute(*args, **kwargs)
      return cursor.fetchall()[0]

  def get_random(self, table):
    return self.query(f'SELECT * FROM {table} ORDER BY RAND( ) LIMIT 1;')

  def add_record(self, record):
    add_review = (
      "INSERT INTO answers (review, aspect, answer, ip) VALUES (%s, %s, %s, %s)"
    )
    with DatabaseConnection(**self.db_config) as cnx:
      cnx.cursor().execute(add_review, record)
      cnx.commit()


db = Database(
  user=os.environ.get('DB_USER'),
  database=os.environ.get('DB_NAME'),
  passwd=os.environ.get('DB_PASSW'),
  raise_on_warnings=True
)


def record_action(number):
  db.add_record((
    session['review_id'],
    session['aspect_id'],
    number,
    request.environ.get('REMOTE_ADDR', request.remote_addr)
  ))


@app.route('/')
def index():
  (_, film_name, text_body, review_id) = db.get_random('reviews')
  (aspect_id, aspect_body) = db.get_random('aspects')
  session['review_id'] = review_id
  session['aspect_id'] = aspect_id
  return render_template(
    "index.html",
    film_name=film_name,
    review=text_body,
    aspect=aspect_body
  )


@app.route('/yes_clicked', methods=['POST'])
def yes_clicked():
  record_action(1)
  return redirect('/')


@app.route('/no_clicked', methods=['POST'])
def no_clicked():
  record_action(0)
  return redirect('/')


@app.route('/absence_clicked', methods=['POST'])
def absence_clicked():
  record_action(2)
  return redirect('/')


@app.route('/skip', methods=['POST'])
def skip():
  return redirect('/')


def main():
  logger = logging.getLogger('waitress')
  logger.setLevel(logging.DEBUG)
  waitress.serve(app, host="0.0.0.0", port=8001)


if __name__ == "__main__": main()
