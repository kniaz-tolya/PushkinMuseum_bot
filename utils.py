from telebot import types
import time
import datetime


def generate_markup_keyboard(training_variants):
    """
    Создаем кастомную клавиатуру для выбора варианта тренировки
    :param training_variants: набор вариантов тренировок
    :return: Объект кастомной клавиатуры
    """
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)

    # Заполняем разметку элементами
    for item in training_variants:
        markup.add(item)
    return markup


def generate_inline_markup(training_variants):
    """
    Создаем кастомную клавиатуру для выбора варианта тренировки
    :param training_variants: набор вариантов тренировок
    :return: Объект кастомной клавиатуры
    """
    markup = types.InlineKeyboardMarkup()

    # Заполняем разметку элементами
    for item in training_variants:
        markup.add(types.InlineKeyboardButton(text=item, callback_data=item))
    return markup


def delete_markup():
    return types.ReplyKeyboardRemove()


def get_book_name_and_link(books, list_link):
    for name in books.keys():
        if books[name] == list_link:
            return name + " - " + list_link


def dateToTimestamp(date, date_format="%Y-%m-%d"):
    return time.mktime(datetime.datetime.strptime(date, date_format).timetuple())


def timestampToDate(timestamp, date_format="%d/%m/%Y"):
    return datetime.datetime.fromtimestamp(
        int(timestamp)).strftime(date_format)
