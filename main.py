# -*- coding: utf-8 -*-

import telebot

import config

bot = telebot.TeleBot(config.token)
bot.stop_polling()


@bot.message_handler(commands=["start"])
def handle_start(message):
    # bot.register_next_step_handler(message, auth.handle_enter_profile)
    bot.send_message(message.from_user.id, "YO!")


@bot.message_handler(content_types=["text"])
def handle_intent(message):
    # bot.send_message(message.from_user.id, "Ага, " + message.text + ", принял, думаю")
    process_command(message)


def process_command(message):
    if "сегодня" in message.text:
        bot.send_message(message.from_user.id, message.text)


bot.polling(none_stop=True)
