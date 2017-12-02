# -*- coding: utf-8 -*-
import datetime
import json
import os
import time
import urllib.request as urllib2

import telebot
from flask import Flask, request

import config
import utils

bot = telebot.TeleBot(config.token)
bot.stop_polling()

HOST = "0.0.0.0"
PORT = os.environ.get('PORT', 8443)

server = Flask(__name__)

last_post_position = 0
user_id = 0
parsed_list = list([])


@bot.message_handler(commands=["start"])
def handle_start(message):
    # bot.register_next_step_handler(message, auth.handle_enter_profile)
    bot.send_message(message.from_user.id, config.welcome_message)
    bot.send_message(message.from_user.id, "Что бы ты хотел узнать?",
                     reply_markup=utils.generate_markup_keyboard(
                         ["Выставки сегодня", "Лекции сегодня", "Концерты сегодня"]))


@bot.message_handler(commands=["links"])
def handle_links(message):
    send_links(message.from_user.id)


def dateToTimestamp(date, date_format="%Y-%m-%d"):
    return time.mktime(datetime.datetime.strptime(date, date_format).timetuple())


intentsToApi = {"expositions": "vystavki", "lections": "lekcii", "concerts": "koncerty"}


def process(event_list, category):
    print(event_list[0])
    return map(lambda event: {"shortDescription": event["shortDescription"], "isFree": event["isFree"],
                              "name": event["name"], "age": event["ageRestriction"],
                              "price": event["price"],
                              # "saleLink": event["saleLink"],
                              "street": event["places"][0]["address"]["street"],
                              "start": event["start"], "end": event["end"]},
               filter(lambda item: item["category"]["sysName"] == intentsToApi[category], event_list))


# "saleLink": event["saleLink"]

def parse_request(date, intent_name, uid):
    response = urllib2.urlopen(config.museum_url.format(dateToTimestamp(date))).read().decode('utf8')
    data1 = json.loads(response)

    global user_id
    user_id = uid
    global parsed_list
    parsed_list = list(process(data1['events'], intent_name))
    build_message_and_send()


def build_message_and_send():
    try:
        is_free = "Посещение бесплатное" if parsed_list[last_post_position]['isFree'] == "true" else "Посещение платное"

        price = str(parsed_list[last_post_position]['price']) + "руб." if is_free == "Посещение платное" else "\n"

        age = "Возрастное ограничение: " + str(parsed_list[last_post_position]["age"]) + "+"

        user_message = "*" + parsed_list[last_post_position]['name'] + "*" + "\n\n" + parsed_list[last_post_position][
            'shortDescription'] + "\n\n" + is_free + " " + price + "\n\n" + age + "\n\n" + \
                       parsed_list[last_post_position][
                           "street"] \
                       # + " \n\n" + "Билеты " + parsed_list[last_post_position]['saleLink']

        bot.send_message(user_id, user_message, parse_mode="Markdown",
                         reply_markup=utils.generate_markup_keyboard(["Ещё"]))

    except IndexError:
        bot.send_message(user_id, "Больше нет(", reply_markup=utils.delete_markup())


def process_command(response):
    data = json.loads(response)
    print(data)
    intent_name = data['result']['metadata']['intentName']
    user_id = data['originalRequest']['data']['message']['chat']['id']

    if intent_name == "more":
        global last_post_position
        last_post_position += 1
        build_message_and_send()
    elif intent_name == "links":
        send_links(user_id)
    else:
        last_post_position = 0
        date = data['result']['parameters']['date']
        if intent_name == "events":
            bot.send_message(user_id, "Что вы хотите посетить?",
                             reply_markup=utils.generate_markup_keyboard(
                                 ["Выставки сегодня", "Лекции сегодня", "Концерты сегодня"]))
        else:
            parse_request(date, intent_name, user_id)


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
