import telebot
from loader import bot
from database.database_handler import create_tables
import handlers
from utils.set_bot_commands import set_default_commands

if __name__ == '__main__':
    create_tables()
    set_default_commands(bot)
    bot.add_custom_filter(telebot.custom_filters.StateFilter(bot))
    bot.infinity_polling()

