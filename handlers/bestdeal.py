from loader import bot
from utils.states import StatesBestdeal
import utils.handler_tools as ht
from telegram_bot_calendar import DetailedTelegramCalendar


@bot.message_handler(commands=['bestdeal'])
def bestdeal(message):
    ht.command_start(message, 'BEST_SELLER', 'bestdeal', StatesBestdeal.location_searching)


@bot.message_handler(state=StatesBestdeal.location_searching)
def best_clarify(message):
    ht.search_location(message, StatesBestdeal.location_clarifying)


@bot.callback_query_handler(state=StatesBestdeal.location_clarifying,
                            func=lambda call: call.data.startswith('loc'),
                            )
def best_ask_date_arrival(call):
    ht.ask_date_arrival(call, StatesBestdeal.arrival_date_ask)


@bot.callback_query_handler(state=StatesBestdeal.arrival_date_ask, func=DetailedTelegramCalendar.func())
def best_calendar_processing_arrival(call):
    ht.calendar_processing_arrival(call, StatesBestdeal.departure_date_ask)


@bot.callback_query_handler(state=StatesBestdeal.departure_date_ask, func=DetailedTelegramCalendar.func())
def best_calendar_processing_departure(call):
    if ht.calendar_processing_departure(call):
        ht.ask_for_min_price(call, StatesBestdeal.price_interval_min)


@bot.message_handler(state=StatesBestdeal.price_interval_min)
def min_price_handle_best(message):
    ht.ask_for_max_price(message, StatesBestdeal.price_interval_max)


@bot.message_handler(state=StatesBestdeal.price_interval_max)
def max_price_handle_best(message):
    ht.ask_for_min_distance(message, StatesBestdeal.distance_interval_min)


@bot.message_handler(state=StatesBestdeal.distance_interval_min)
def min_distance_handle_best(message):
    ht.ask_for_max_distance(message, StatesBestdeal.distance_interval_max)


@bot.message_handler(state=StatesBestdeal.distance_interval_max)
def max_distance_handle_best(message):
    if ht.handle_max_distance(message):
        ht.ask_for_hotel_amount(message.from_user.id, StatesBestdeal.page_size_asking)


@bot.message_handler(state=StatesBestdeal.page_size_asking)
def showing_results_best(message):
    ht.showing_results(message)


@bot.callback_query_handler(func=lambda call: call.data.startswith('photo'))
def best_ask_photo_amount(call):
    ht.ask_photo(call, StatesBestdeal.photos_amount)


@bot.message_handler(state=StatesBestdeal.photos_amount)
def best_send_photos(message):
    ht.send_photos(message)
