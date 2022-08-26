from loader import bot
from utils.states import StatesHighprice
import utils.handler_tools as ht
from telegram_bot_calendar import DetailedTelegramCalendar


@bot.message_handler(commands=['highprice'])
def highprice(message):
    ht.command_start(message, 'PRICE_HIGHEST_FIRST', 'highprice', StatesHighprice.location_searching)


@bot.message_handler(state=StatesHighprice.location_searching)
def high_clarify(message):
    ht.search_location(message, StatesHighprice.location_clarifying)


@bot.callback_query_handler(state=StatesHighprice.location_clarifying,
                            func=lambda call: call.data.startswith('loc'),
                            )
def high_ask_date_arrival(call):
    ht.ask_date_arrival(call, StatesHighprice.arrival_date_ask)


@bot.callback_query_handler(state=StatesHighprice.arrival_date_ask, func=DetailedTelegramCalendar.func())
def high_calendar_processing_arrival(call):
    ht.calendar_processing_arrival(call, StatesHighprice.departure_date_ask)


@bot.callback_query_handler(state=StatesHighprice.departure_date_ask, func=DetailedTelegramCalendar.func())
def high_calendar_processing_departure(call):
    if ht.calendar_processing_departure(call):
        ht.ask_for_hotel_amount(call.from_user.id, StatesHighprice.page_size_asking)


@bot.message_handler(state=StatesHighprice.page_size_asking)
def high_showing_results(message):
    ht.showing_results(message)


@bot.callback_query_handler(func=lambda call: call.data.startswith('photo'))
def high_ask_photo_amount(call):
    ht.ask_photo(call, StatesHighprice.photos_amount)


@bot.message_handler(state=StatesHighprice.photos_amount)
def high_send_photos(message):
    ht.send_photos(message)
