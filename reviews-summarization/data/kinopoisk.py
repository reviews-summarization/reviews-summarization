import argparse
import json
from pathlib import Path

import bs4
import requests
from selenium.webdriver.common.by import By
from seleniumwire import webdriver

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
                    'Chrome/123.0.0.0 Safari/537.36',
      'Accept': 'text/html',
      'Accept-Language': 'ru,en-us;q=0.7,en;q=0.3',
      'Accept-Encoding': 'utf-8',
      'Accept-Charset': 'utf-8',
      'Keep-Alive': '300',
      'Connection': 'keep-alive',
      'Referer': 'http://www.kinopoisk.ru/',
      'Cookie':  self.cookies
    }

  def top_films(self):
    film_ids = []
    browser = webdriver.Chrome()

    def interceptor(request):
      for key, value in self.headers.items():
        request.headers[key] = value
      del request.headers['Referer']
      request.headers['Referer'] = \
        'https://www.kinopoisk.ru/lists/movies/top250/'

    browser.request_interceptor = interceptor
    for page_number in range(1, 6):
      page_url = f'https://www.kinopoisk.ru/lists/movies/top250/' \
                 f'?page={page_number}'
      browser.get(page_url)
      urls = browser.find_elements(
        By.CLASS_NAME, 'base-movie-main-info_link__YwtP1'
      )
      for url in urls:
        link = url.get_attribute('href')
        film_id = link.split('/')[-2]
        film_ids.append(film_id)

    browser.quit()
    return film_ids


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
  top_films_ids = kp.top_films()
  all_reviews = {}
  for id_film in top_films_ids:
    all_reviews[id_film] = kp.get_reviews(id_film)
  args.store_path.write_text(json.dumps(all_reviews, ensure_ascii=False))


if __name__ == '__main__': main(parse_args())
