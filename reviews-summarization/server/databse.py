import os
import functools

import mysql.connector


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
    return self.list_query(*args, **kwargs)[0]

  def list_query(self, *args, **kwargs):
    with DatabaseConnection(**self.db_config) as cnx:
      cursor = cnx.cursor()
      cursor.execute(*args, **kwargs)
      return cursor.fetchall()

  def get_random(self, table):
    return self.query(f'SELECT * FROM {table} ORDER BY RAND( ) LIMIT 1;')

  def get(self, table, entity_id):
    return self.query(
      f'SELECT * FROM {table} WHERE id LIKE \'%{entity_id}%%\';'
    )

  @functools.lru_cache()
  def all(self, table):
    return self.list_query(f'SELECT * FROM {table};')

  def add_record(self, record):
    add_review = (
      "INSERT INTO answers (review, aspect, answer, ip, session) " \
        "VALUES (%s, %s, %s, %s, %s)"
    )
    with DatabaseConnection(**self.db_config) as cnx:
      cnx.cursor().execute(add_review, record)
      cnx.commit()

def make_database():
  return Database(
    user=os.environ.get('DB_USER'),
    database=os.environ.get('DB_NAME'),
    passwd=os.environ.get('DB_PASSW'),
    raise_on_warnings=True
  )
