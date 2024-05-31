import logging
import os
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, \
  CommandHandler, MessageHandler, filters
from dotenv import load_dotenv

import process

logging.basicConfig (
  format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
  level=logging.INFO
)

def get_filmid(link):
  splited_link = link.split('/')
  film_id = splited_link[splited_link.index('film') + 1]
  return film_id


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
  await context.bot.send_message(
    chat_id=update.effective_chat.id,
    text="Отправьте ссылку на фильм с кинопоиска https://www.kinopoisk.ru"
  )


async def reader(update: Update, context: ContextTypes.DEFAULT_TYPE):
  logging.info(f'Processing: {update.message.text}, from: {update.message.from_user}')
  link = update.message.text
  film_id = get_filmid(link)
  await context.bot.send_message(
    chat_id=update.effective_chat.id,
    text=process.predict_film(film_id)
  )


def main():
  load_dotenv()
  application = ApplicationBuilder().token(os.getenv('TELEGRAM_TOKEN')).build()

  start_handler = CommandHandler('start', start)
  application.add_handler(start_handler)

  reader_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), reader)
  application.add_handler(reader_handler)

  application.run_polling()


if __name__ == '__main__': main()

