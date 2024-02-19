import argparse
import json
from pathlib import Path

import bs4
import requests

CUR_DIR = Path(__file__).parent

class Kinopoisk:
  ENDPOINT = 'https://www.kinopoisk.ru/'

  def __init__(self, cookies) -> None:
    self.cookies = cookies

  @property
  def headers(self):
    return {
      'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
                    'AppleWebKit/537.36 (KHTML, like Gecko) '
                    'Chrome/122.0.0.0 Safari/537.36',
      'Accept': 'text/html',
      'Accept-Language': 'ru,en-us;q=0.7,en;q=0.3',
      'Accept-Encoding': 'utf-8',
      'Accept-Charset': 'utf-8',
      'Keep-Alive': '300',
      'Connection': 'keep-alive',
      'Referer': 'http://www.kinopoisk.ru/',
      'Cookie':  self.cookies
    }

  def top_films(self) -> list[str]:
    assert False, 'Not implemented'

  def _get_reviews(self, film_id, page_number):
    method = f'film/{film_id}/reviews/page/{page_number}/perpage/100/'
    resp = requests.get(self.ENDPOINT + method, headers=self.headers)
    soup = bs4.BeautifulSoup(resp.text, 'html.parser')
    reviews = soup.find_all('span', {'itemprop': 'reviewBody'})
    return [x.text for x in reviews]

  def get_reviews(self, film_id):
    reviews = []
    for page_number in range(1, 100):
      current = self._get_reviews(film_id, page_number)
      if not current: break
      reviews.extend(current)
    return reviews


def parse_args():
  parser = argparse.ArgumentParser()
  parser.add_argument(
    '--cookie-path',
    type=Path,
    default=CUR_DIR / '.cookies',
    help='Path to file with kinopoisk cookies'
  )
  parser.add_argument(
    '--store-path',
    type=Path,
    default=CUR_DIR / 'data.json',
    help='Store json with reviews'
  )
  return parser.parse_args()


def main(args):
  kp = Kinopoisk(args.cookie_path.read_text().strip())
  all_reviews = {
    film_id: kp.get_reviews(film_id)
    for film_id in range(435, 436)
  }
  args.store_path.write_text(json.dumps(all_reviews, ensure_ascii=False))
  print(all_reviews[435][:10])


if __name__ == '__main__': main(parse_args())
