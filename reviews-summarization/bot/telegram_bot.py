import logging
import sys
from pathlib import Path
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    MessageHandler,
    filters
)


PATH = (Path(__file__).parents[1] / 'data').resolve()
sys.path.insert(0, str(PATH))

logging.basicConfig (
  format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
  level=logging.INFO
)


def get_url(link):
  splited_link = link.split('/')
  film_id = splited_link[splited_link.index('film') + 1]
  return film_id


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
  await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Отправьте ссылку на фильм с кинопоиска "
             "https://www.kinopoisk.ru/?utm_referrer=www.google.com"
    )

async def reader(update: Update, context: ContextTypes.DEFAULT_TYPE):
  link = update.message.text
  film_id = get_url(link)

  await context.bot.send_message(chat_id=update.effective_chat.id, text=film_id)



if __name__ == '__main__':
  application = (
      ApplicationBuilder()
      .token('6477280252:AAH3wU2QOEuRFa9JZelVU1AKOA4LzIAe4OE')
      .build()
  )

  start_handler = CommandHandler('start', start)
  application.add_handler(start_handler)

  reader_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), reader)
  application.add_handler(reader_handler)

  application.run_polling()