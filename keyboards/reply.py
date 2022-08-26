from telebot.types import KeyboardButton, ReplyKeyboardMarkup


def reply_keyboard(button_list):
    markup = ReplyKeyboardMarkup()
    for button in button_list:
        markup.add(KeyboardButton(button))
    return markup
