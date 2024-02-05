import telebot
from config import load_config
import time
bot = telebot.TeleBot(load_config().tg_bot.token)  # тут токен
post_channel = '-1002132280918'


# простейший синхронный бот на одну команду
def post_msg(text) -> None:
    while 1:
        try:
            bot.send_message(chat_id=post_channel, text=text)
            time.sleep(1)
            return
        # если слишком много запросов
        except telebot.apihelper.ApiTelegramException as e:
            print('много запросов:\n', e)
            print('text:', text)
            time.sleep(20)
