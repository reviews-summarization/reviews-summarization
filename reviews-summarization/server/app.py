import os
import secrets
import functools
import logging

import mysql.connector
import waitress
from flask import Flask, render_template, request, url_for, session  # pylint: disable=unused-import

app = Flask(__name__)
app.secret_key = secrets.token_hex()

class Database:
  @functools.cached_property
  def cnx(self):
    return mysql.connector.connect(
      user=os.environ.get('DB_USER'),
      database=os.environ.get('DB_NAME'),
      passwd=os.environ.get('DB_PASSW')
    )

  def query(self, *args, **kwargs):
    cursor = self.cnx.cursor()
    cursor.execute(*args, **kwargs)
    return cursor.fetchall()[0]

  def get_random(self, table):
    return self.query(f'SELECT * FROM {table} ORDER BY RAND( ) LIMIT 1;')

  def add_record(self, record):
    add_review = (
      "INSERT INTO answers (review, aspect, answer, ip) VALUES (%s, %s, %s, %s)"
    )
    cursor = self.cnx.cursor()
    cursor.execute(add_review, record)
    self.cnx.commit()


db = Database()
def review_page():
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


def retrieve_action(number):
  db.add_record((
    session['review_id'],
    session['aspect_id'],
    number,
    request.environ.get('REMOTE_ADDR', request.remote_addr)
  ))


@app.route('/')
def index():
  return review_page()


@app.route('/yes_clicked', methods=['POST'])
def yes_clicked():
  retrieve_action(1)
  return review_page()


@app.route('/no_clicked', methods=['POST'])
def no_clicked():
  retrieve_action(0)
  return review_page()


@app.route('/absence_clicked', methods=['POST'])
def absence_clicked():
  retrieve_action(2)
  return review_page()


def main():
  logger = logging.getLogger('waitress')
  logger.setLevel(logging.DEBUG)
  waitress.serve(app, host="0.0.0.0", port=8001)


if __name__ == "__main__": main()
