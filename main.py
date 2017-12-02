# -*- coding: utf-8 -*-
import os

import telebot
from flask import Flask, request

import config
import utils

bot = telebot.TeleBot(config.token)
bot.stop_polling()

# HOST = "0.0.0.0"
# PORT = os.environ.get('PORT', 8443)
#
# server = Flask(__name__)


@bot.message_handler(commands=["start"])
def handle_start(message):
    # bot.register_next_step_handler(message, auth.handle_enter_profile)
    bot.send_message(message.from_user.id, "Привет! Тебя приветсвует бот-помощник Пушкинского Музея\n")
    bot.send_message(message.from_user.id, "Что бы ты хотел узнать?",
                     reply_markup=utils.generate_markup_keyboard(["События сегодня", "Ссылки на ресурсы"]))


@bot.message_handler(content_types=["text"])
def handle_intent(message):
    # bot.send_message(message.from_user.id, "Ага, " + message.text + ", принял, думаю")
    process_command(message)


def process_command(message):
    if "сегодня" in message.text:
        bot.send_message(message.from_user.id, message.text)


# @server.route('/bot', methods=['POST'])
# def get_message():
#     bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
#     return '/bot', 200
#
#
# @server.route('/')
# def webhook_handler():
#     bot.remove_webhook()
#     bot.set_webhook(url=config.heroku_webhook)
#     status_msg = "i'm live. listening on %s:%s" % (HOST, PORT)
#     return status_msg, 200

bot.remove_webhook()
bot.polling(none_stop=True)

# # Remove webhook, it fails sometimes the set if there is a previous webhook
# bot.remove_webhook()
#
# # Set webhook
# bot.set_webhook(url=config.heroku_webhook)
#
# # bot.polling(none_stop=True)
# server.run(host=HOST, port=PORT)
