from telebot.handler_backends import State, StatesGroup


class StatesLowprice(StatesGroup):
    location_searching = State()
    location_clarifying = State()
    arrival_date_ask = State()
    departure_date_ask = State()
    page_size_asking = State()
    photos_amount = State()


class StatesHighprice(StatesGroup):
    location_searching = State()
    location_clarifying = State()
    arrival_date_ask = State()
    departure_date_ask = State()
    page_size_asking = State()
    photos_amount = State()


class StatesBestdeal(StatesGroup):
    location_searching = State()
    location_clarifying = State()
    arrival_date_ask = State()
    departure_date_ask = State()
    page_size_asking = State()
    photos_amount = State()
    price_interval_min = State()
    price_interval_max = State()
    distance_interval_min = State()
    distance_interval_max = State()
