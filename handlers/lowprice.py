from loader import bot, storage
from utils.states import StatesLowprice
import utils.handler_tools as ht
from telegram_bot_calendar import DetailedTelegramCalendar


@bot.message_handler(commands=['lowprice'])
def lowprice(message):
    ht.command_start(message, 'PRICE', 'lowprice', StatesLowprice.location_searching)


@bot.message_handler(state=StatesLowprice.location_searching)
def low_clarify(message):
    ht.search_location(message, StatesLowprice.location_clarifying)


@bot.callback_query_handler(state=StatesLowprice.location_clarifying,
                            func=lambda call: call.data.startswith('loc'),
                            )
def low_ask_date_arrival(call):
    ht.ask_date_arrival(call, StatesLowprice.arrival_date_ask)


@bot.callback_query_handler(state=StatesLowprice.arrival_date_ask, func=DetailedTelegramCalendar.func())
def low_calendar_processing_arrival(call):
    ht.calendar_processing_arrival(call, StatesLowprice.departure_date_ask)


@bot.callback_query_handler(state=StatesLowprice.departure_date_ask, func=DetailedTelegramCalendar.func())
def low_calendar_processing_departure(call):
    if ht.calendar_processing_departure(call):
        ht.ask_for_hotel_amount(call.from_user.id, StatesLowprice.page_size_asking)


@bot.message_handler(state=StatesLowprice.page_size_asking)
def low_showing_results(message):
    ht.showing_results(message)


@bot.callback_query_handler(func=lambda call: call.data.startswith('photo'))
def low_ask_photo_amount(call):
    ht.ask_photo(call, StatesLowprice.photos_amount)


@bot.message_handler(state=StatesLowprice.photos_amount)
def low_send_photos(message):
    ht.send_photos(message)
