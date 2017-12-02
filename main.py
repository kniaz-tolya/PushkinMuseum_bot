# -*- coding: utf-8 -*-
import json
import os

import telebot
from flask import Flask, request

import config
import utils

import time
import datetime

bot = telebot.TeleBot(config.token)
bot.stop_polling()

HOST = "0.0.0.0"
PORT = os.environ.get('PORT', 8443)

server = Flask(__name__)


@bot.message_handler(commands=["start"])
def handle_start(message):
    # bot.register_next_step_handler(message, auth.handle_enter_profile)
    bot.send_message(message.from_user.id, config.welcome_message)
    bot.send_message(message.from_user.id, "Что бы ты хотел узнать?",
                     reply_markup=utils.generate_markup_keyboard(["Выставки", "Лекции", "Концерты"]))


@bot.message_handler(commands=["links"])
def handle_links(message):
    send_links(message.from_user.id)


# @bot.message_handler(content_types=["text"])
# def handle_intent(message):
#     bot.send_message(message.from_user.id, "Ага, " + message.text + ", принял, думаю")
#     # process_command(message)


def process_command(response):
    data = json.loads(response)
    print(data)

    intent_name = data['result']['metadata']['intentName']
    user_id = data['originalRequest']['data']['message']['chat']['id']
    if intent_name == "events":
        bot.send_message(user_id, "Что вы хотите посетить?",
                         reply_markup=utils.generate_markup_keyboard(["Выставки", "Лекции", "Концерты"]))
    elif intent_name == "links":
        send_links(user_id)
    else:
        bot.send_message(user_id, ":)", reply_markup=utils.delete_markup())


def send_links(user_id):
    bot.send_message(user_id, "[Новости](http://www.arts-museum.ru/museum/news/index.php)", parse_mode="Markdown")
    bot.send_message(user_id, "[Контакты](http://www.arts-museum.ru/museum/contacts/index.php)",
                     parse_mode="Markdown")
    bot.send_message(user_id, "[Билеты](https://tickets.arts-museum.ru/ru/)", parse_mode="Markdown")
    bot.send_message(user_id, "[Режим работы](http://www.arts-museum.ru/visitors/contact/index.php)",
                     parse_mode="Markdown")


@server.route('/bot', methods=['POST'])
def post_message():
    req = request.stream.read().decode("utf-8")
    bot.process_new_updates([telebot.types.Update.de_json(req)])
    return '/bot', 200


@server.route('/dialog', methods=['POST', 'GET'])
def dialog_message():
    req = request.stream.read().decode("utf-8")
    print(req)
    process_command(req)
    return '/dialog', 200


@server.route('/bot', methods=['GET'])
def get_message():
    req = request.stream.read().decode("utf-8")
    print(req)
    return '/bot', 200


@server.route('/')
def webhook_handler():
    bot.remove_webhook()
    bot.set_webhook(url=config.heroku_webhook)
    status_msg = "i'm live. listening on %s:%s" % (HOST, PORT)
    return status_msg, 200


# bot.remove_webhook()
# bot.polling(none_stop=True)

# Remove webhook, it fails sometimes the set if there is a previous webhook
bot.remove_webhook()

# Set webhook
bot.set_webhook(url=config.heroku_webhook)

# bot.polling(none_stop=True)
server.run(host=HOST, port=PORT)


def dateToTimestamp(date, date_format="%Y-%m-%d"):
    return time.mktime(datetime.datetime.strptime(date, date_format).timetuple())

intentsToApi = {"expositions": "vystavki", "lections": "lekcii", "concerts": "koncerty"}

def proccess(list, category):
    return map(lambda event: {"shortDescription": event["shortDescription"], "isFree": event["isFree"]},
               filter(lambda item: item["category"]["sysName"] == intentsToApi[category], list))