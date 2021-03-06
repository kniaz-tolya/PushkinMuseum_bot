# -*- coding: utf-8 -*-
import json
import os
import urllib.request as urllib2

import telebot
from flask import Flask, request

import config
import utils

from utils import dateToTimestamp, timestampToDate

bot = telebot.TeleBot(config.token)
bot.stop_polling()

HOST = "0.0.0.0"
PORT = os.environ.get('PORT', 8443)

server = Flask(__name__)

sessionContext = {}


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


def parse_request(date, intent_name, uid):
    response = urllib2.urlopen(config.museum_url.format(dateToTimestamp(date))).read().decode('utf8')
    data1 = json.loads(response)

    parsed_list = list(process(data1['events'], intent_name))

    sessionContext[uid] = {'data': parsed_list, 'index': 0}

    build_message_and_send(uid)


def build_message_and_send(uid):

    context = sessionContext[uid]
    last_post_position = context['index']
    parsed_list = context['data']

    if last_post_position >= len(parsed_list):
        bot.send_message(uid, "Больше нет(", reply_markup=utils.delete_markup())
        return

    is_free = "Посещение бесплатное" if parsed_list[last_post_position]['isFree'] == "true" else "Посещение платное"

    price = str(parsed_list[last_post_position]['price']) + "руб." if is_free == "Посещение платное" else "\n"

    age = "Возрастное ограничение: " + str(parsed_list[last_post_position]["age"]) + "+"

    # period = "С " + timestampToDate(parsed_list[last_post_position]["start"]) + " по " + timestampToDate(parsed_list[last_post_position]["end"])

    user_message = "*" + parsed_list[last_post_position]['name'] + "*" + "\n\n" + parsed_list[last_post_position][
        'shortDescription'] + "\n\n" + is_free + " " + price + "\n\n" + age + "\n\n" + \
                   parsed_list[last_post_position][
                       "street"] \
        # + "\n\n" + period
    # + " \n\n" + "Билеты " + parsed_list[last_post_position]['saleLink']

    bot.send_message(uid, user_message, parse_mode="Markdown",
                     reply_markup=utils.generate_markup_keyboard(["Ещё"]))


def process_command(response):
    data = json.loads(response)
    print(data)
    intent_name = data['result']['metadata']['intentName']
    user_id = data['originalRequest']['data']['message']['chat']['id']

    if intent_name == "more":
        sessionContext[user_id]['index'] = sessionContext[user_id]['index'] + 1
        build_message_and_send(user_id)
    elif intent_name == "links":
        send_links(user_id)
    else:
        else_case(data, intent_name, user_id)


def else_case(data, intent_name, user_id):
    date = data['result']['parameters']['date']
    if intent_name == "events":
        what_you_want_to_visit(user_id, "Что вы хотите посетить?")
    else:
        parse_request(date, intent_name, user_id)


def process_more_case(user_id, data, intent_name):
    if sessionContext.__contains__(user_id):
        parsed_list = sessionContext[user_id]
        last_post_position = int(sessionContext[user_id]['index']) + 1
        if last_post_position < len(parsed_list):
            build_message_and_send(user_id)
        else:
            else_case(data, intent_name, user_id)
    else:
        what_you_want_to_visit(user_id, "Сначала выберите, что вы хотите посетить?")


def what_you_want_to_visit(user_id, text):
    bot.send_message(user_id, text,
                     reply_markup=utils.generate_markup_keyboard(
                         ["Выставки сегодня", "Лекции сегодня", "Концерты сегодня"]))


def send_links(user):
    bot.send_message(user, "[Новости](http://www.arts-museum.ru/museum/news/index.php)", parse_mode="Markdown")
    bot.send_message(user, "[Контакты](http://www.arts-museum.ru/museum/contacts/index.php)",
                     parse_mode="Markdown")
    bot.send_message(user, "[Билеты](https://tickets.arts-museum.ru/ru/)", parse_mode="Markdown")
    bot.send_message(user, "[Режим работы](http://www.arts-museum.ru/visitors/contact/index.php)",
                     parse_mode="Markdown")


@server.route('/bot', methods=['POST'])
def post_message():
    req = request.stream.read().decode("utf-8")
    bot.process_new_updates([telebot.types.Update.de_json(req)])
    return '/bot', 200


@server.route('/dialog', methods=['GET'])
def dialog_message_get():
    req = request.stream.read().decode("utf-8")
    print(req)
    bot.process_new_updates([telebot.types.Update.de_json(req)])
    return '/dialog', 200


@server.route('/dialog', methods=['POST'])
def dialog_message_post():
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
