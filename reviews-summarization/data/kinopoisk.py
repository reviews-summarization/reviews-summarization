import argparse
from pathlib import Path
import uuid

import database

import bs4
import requests
from selenium.webdriver.common.by import By
from seleniumwire import webdriver

CUR_DIR = Path(__file__).parent
ASPECTS = {
  'Режиссерская работа': 'director',
  'Саундтрек/музыка': 'music',
  'Актерская игра': 'actors',
  'Визуальные эффекты': 'visuals',
  'Эмоциональное воздействие': 'emotional',
  'Раскрытие темы': 'topic',
  'Оригинальность сюжета': 'originality',
  'Юмор': 'humour',
  'Дизайн постановки/костюмов': 'design',
}


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

  @property
  def browser(self): return webdriver.Chrome()

  def _fix_headers(self, request):
    for key, value in self.headers.items():
      request.headers[key] = value
    request.headers['Referer'] = f'{self.ENDPOINT}lists/movies/top250/'

  def top_films(self):
    def interceptor(request): self._fix_headers(request)
    self.browser.request_interceptor = interceptor

    film_ids = []
    for page_number in range(1, 6):
      self.browser.get(
        f'{self.ENDPOINT}lists/movies/top250/?page={page_number}'
      )
      urls = self.browser.find_elements(
        By.CLASS_NAME, 'base-movie-main-info_link__YwtP1'
      )
      for url in urls:
        film_ids.append(url.get_attribute('href').split('/')[-2])

    self.browser.quit()
    return film_ids

  def _worst_films(self, page):
    method = \
      f'top/navigator/m_act[rating]/1%3A4/order/rating/page/{page}/#results'
    resp = requests.get(self.ENDPOINT + method, headers=self.headers)
    soup = bs4.BeautifulSoup(resp.text, 'html.parser')
    return set([
      x.get('data-kp-film-id')
      for x in soup.find_all('div', class_='js-ott-widget')
    ])

  def worst_films(self):
    all_films = set()
    for i in range(1, 100):
      films = self._worst_films(i)
      if not list(films): break
      all_films |= films
    return all_films


  def film_name(self, film_id):
    def interceptor(request): self._fix_headers(request)
    self.browser.request_interceptor = interceptor
    self.browser.get(f'{self.ENDPOINT}film/{film_id}')
    urls = self.browser.find_elements(By.XPATH, '//span[@data-tid]')

    titles = []
    def check_string(s):
      for el in s:
        if el < '0' or el > '9':
          return True
      return False

    for url in urls:
      if url.text and check_string(url.text): titles.append(url.text)

    return titles[0]

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
  parser.add_argument('--aspects', default=False, action='store_true')
  parser.add_argument('--reviews', default=False, action='store_true')
  return parser.parse_args()


def make_kinopoisk():
  return Kinopoisk((CUR_DIR / '.cookies').read_text().strip())


def store_aspects(db):
  aspects_data = [(str(uuid.uuid4()), x) for x in ASPECTS]
  print(aspects_data)
  for aspect in aspects_data:
    db.add_record('aspects', aspect)


def main(args):
  kp = make_kinopoisk()
  db = database.make_database()
  if args.aspects: store_aspects(db)
  if not args.reviews: return
  for film_id in kp.top_films() + kp.worst_films():
    for review in kp.get_reviews(film_id):
      db.add_record(
        'reviews',
        (int(film_id), kp.film_name(film_id), review, str(uuid.uuid4()))
      )


if __name__ == '__main__': main(parse_args())
