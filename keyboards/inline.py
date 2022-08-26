from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton


def inline_keyboard(button_dict):
    markup = InlineKeyboardMarkup()
    for button in button_dict.items():
        markup.add(InlineKeyboardButton(text=button[0], callback_data=button[1]))
    return markup
