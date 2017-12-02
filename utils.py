from telebot import types


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
