from flask import Flask, render_template, url_for  # noqa # pylint: disable=unused-import

app = Flask(__name__)

@app.route('/')
def index():
  return render_template("index.html")


@app.route('/yes_clicked', methods=['POST'])
def yes_clicked():
    # add to db
  return render_template("index.html")


@app.route('/no_clicked', methods=['POST'])
def no_clicked():
    # add to db
  return render_template("index.html")


if __name__ == "__main__":
  import logging
  logger = logging.getLogger('waitress')
  logger.setLevel(logging.DEBUG)
  from waitress import serve
  serve(app, host="0.0.0.0", port=8001)

