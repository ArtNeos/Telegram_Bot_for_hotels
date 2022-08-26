from loader import bot
from utils.request import locations_search, hotel_list, get_photos_urls
import keyboards
from telegram_bot_calendar import DetailedTelegramCalendar
from telebot.types import InputMediaPhoto, Message, CallbackQuery
from telebot.handler_backends import State
from database.database_handler import set_history, set_hotels
import datetime


class MyCalendar(DetailedTelegramCalendar):
    prev_button = "⬅️"
    next_button = "➡️"
    empty_month_button = ""
    empty_year_button = ""


def command_start(message: Message, sort_order: str, command: str, next_state: State) -> None:
    """Функция обрабатывает команду поиска и приглашает ввести название города"""
    bot.send_message(message.from_user.id, 'Введите название города')
    bot.set_state(message.from_user.id, next_state)
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['page'] = 1
        data['adults'] = 1
        data['sort_order'] = sort_order
        data['command'] = command


def search_location(message: Message, next_state: State) -> None:
    """Функция обрабатывает введеное название города и предлагает выбрать один из найденных вариантов"""
    locations = locations_search(message.text)
    if bool(locations) is False:
        bot.send_message(message.from_user.id, 'По данному запросу ничего не удалось найти')
        bot.delete_state(message.from_user.id)
        return
    with bot.retrieve_data(message.from_user.id) as data:
        data['locations'] = locations
    markup = keyboards.inline.inline_keyboard({name: 'loc' + str(hotel_id) + ' ' + name
                                               for name, hotel_id in data['locations'].items()})
    bot.send_message(message.from_user.id, 'Выберите вариант из списка', reply_markup=markup)
    bot.set_state(message.from_user.id, next_state)


def ask_date_arrival(call: CallbackQuery, next_state: State) -> None:
    """Функция обрабатывает выбранную пользователем локацию и отправляет приглашение выбрать дату прибытия"""
    step_dict = {'y': 'год', 'm': 'месяц', 'd': 'день'}
    with bot.retrieve_data(call.from_user.id) as data:
        info = call.data[3:].split()
        data['id'] = info[0]
        data['city'] = info[1]
    calendar, step = MyCalendar(min_date=datetime.date.today()).build()
    bot.send_message(call.from_user.id, f"Укажите дату прибытия:\nВыберите {step_dict[step]}", reply_markup=calendar)
    bot.set_state(call.from_user.id, next_state)


def calendar_processing_arrival(call: CallbackQuery, next_state: State) -> None:
    """Функция обработки взаимодействия с календарем, после выбора даты отправляет приглашение выбрать дату отбытия"""
    step_dict = {'y': 'год', 'm': 'месяц', 'd': 'день'}
    result, key, step = MyCalendar(locale='ru', min_date=datetime.date.today()).process(call.data)
    if not result and key:
        bot.edit_message_text(f"Укажите дату прибытия:\nВыберите {step_dict[step]}",
                              call.message.chat.id,
                              call.message.message_id,
                              reply_markup=key)
    elif result:
        bot.edit_message_text(f"Вы выбрали {result}",
                              call.message.chat.id,
                              call.message.message_id)
        with bot.retrieve_data(call.from_user.id) as data:
            data['arrival'] = result
        calendar, step = MyCalendar(min_date=datetime.date.today()).build()
        bot.send_message(call.from_user.id, f"Укажите дату отбытия:\nВыберите {step_dict[step]}", reply_markup=calendar)
        bot.set_state(call.from_user.id, next_state)


def calendar_processing_departure(call: CallbackQuery) -> bool:
    """Функция обработки взаимодействия с календарем,
    возвращает True когда работа с календарем завершена и False иначе"""
    step_dict = {'y': 'год', 'm': 'месяц', 'd': 'день'}
    result, key, step = MyCalendar(locale='ru', min_date=datetime.date.today()).process(call.data)
    if not result and key:
        bot.edit_message_text(f"Укажите дату отбытия:\nВыберите {step_dict[step]}",
                              call.message.chat.id,
                              call.message.message_id,
                              reply_markup=key)
        return False
    elif result:
        with bot.retrieve_data(call.from_user.id) as data:
            if result <= data['arrival']:
                calendar, step = MyCalendar(min_date=datetime.date.today()).build()
                bot.edit_message_text("Дата отбытия не может быть раньше даты прибытия\n"
                                      f"Укажите дату отбытия:\nВыберите {step_dict[step]}",
                                      call.message.chat.id,
                                      call.message.message_id,
                                      reply_markup=calendar
                                      )
                return False
            bot.edit_message_text(f"Вы выбрали {result}",
                                  call.message.chat.id,
                                  call.message.message_id)

            data['departure'] = result
            data['duration'] = (data['departure'] - data['arrival']).days
        return True


def ask_for_min_price(call: CallbackQuery, next_state: State) -> None:
    """Функция отправляет приглашение ввести минимальную цену за ночь"""
    bot.send_message(call.from_user.id,
                     "Укажите минимальную цену за ночь в USD(для отделения целой части используйте точку")
    bot.set_state(call.from_user.id, next_state)


def ask_for_max_price(message: Message, next_state: State) -> None:
    """Функция обрабатывает минимальную цену за ночь и отправляет приглашение ввести максимальную"""
    if not message.text.isdigit():
        bot.send_message(message.from_user.id, "Не удалось распознать число!\n"
                                               "Введите минимальную цену за ночь в USD")
        return
    if not (0 <= int(message.text)):
        bot.send_message(message.from_user.id, "Цена отеля за ночь не может быть"
                                               "отрицательной.\n"
                                               "Введите минимальную цену за ночь в USD")
        return
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['min_price'] = int(message.text)
    bot.send_message(message.from_user.id, "Теперь укажите максимальную цену за ночь в USD"
                                           "(для отделения целой части используйте точку")
    bot.set_state(message.from_user.id, next_state)


def ask_for_min_distance(message: Message, next_state: State) -> None:
    """Функция обрабатывает максимальную цену за ночь и
    отправляет приглашение ввести минимальное расстояние до центра города"""
    if not message.text.isdigit():
        bot.send_message(message.from_user.id, "Не удалось распознать число!\n"
                                               "Введите максимальную цену за ночь в USD")
        return
    if not (0 <= int(message.text)):
        bot.send_message(message.from_user.id, "Цена отеля за ночь не может быть"
                                               "отрицательной.\n"
                                               "Введите максимальную цену за ночь в USD")
        return
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        if not (data['min_price'] <= int(message.text)):
            bot.send_message(message.from_user.id, "Максимальная цена отеля за ночь не может быть"
                                                   "меньше минимальной.\n"
                                                   "Введите максимальную цену за ночь в USD")
            return
        data['max_price'] = int(message.text)
    bot.send_message(message.from_user.id, "Укажите минимальное расстояние до центра города в метрах")
    bot.set_state(message.from_user.id, next_state)


def ask_for_max_distance(message: Message, next_state: State) -> None:
    """Функция обрабатывает минимальное расстояние до центра города и
    отправляет приглашение ввести максимальное"""
    if not message.text.isdigit():
        bot.send_message(message.from_user.id, "Не удалось распознать число!\n"
                                               "Введите минимальное расстояние до центра города в метрах")
        return
    if not (0 <= int(message.text)):
        bot.send_message(message.from_user.id, "Расстояние до центра города не может быть"
                                               "отрицательным.\n"
                                               "Введите минимальное расстояние до центра города в метрах")
        return
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['min_distance'] = int(message.text)
    bot.send_message(message.from_user.id, "Теперь укажите максимальное расстояние до центра города в метрах")
    bot.set_state(message.from_user.id, next_state)


def handle_max_distance(message: Message) -> bool:
    """Функция обрабатывет максимальное расстояние до центра города и возвращает True при его корректном значении,
    иначе False """
    if not message.text.isdigit():
        bot.send_message(message.from_user.id, "Не удалось распознать число!\n"
                                               "Введите максимальное расстояние до центра города в метрах")
        return False
    if not (0 <= int(message.text)):
        bot.send_message(message.from_user.id, "Расстояние до центра города не может быть"
                                               "отрицательным.\n"
                                               "Введите максимальное расстояние до центра города в метрах")
        return False
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        if not (data['min_distance'] <= int(message.text)):
            bot.send_message(message.from_user.id, "Максимальное расстояние до центра не может быть"
                                                   "меньше минимального.\n"
                                                   "Введите максимальное расстояние до центра города в км")
            return False
        data['max_distance'] = int(message.text)
        return True


def ask_for_hotel_amount(user_id: int, next_state: State) -> None:
    """Функция отправляет приглашение ввести количество отображаемых отелей"""
    bot.send_message(user_id, "Укажите количество отображаемых отелей")
    bot.set_state(user_id, next_state)


def showing_results(message: Message) -> None:
    """Функция отображает результат поиска отелей по ранее введенным критериям"""
    if not message.text.isdigit():
        bot.send_message(message.from_user.id, "Не удалось распознать число!\n"
                                               "Введите число отображаемых отелей")
        return
    if not (0 < int(message.text) < 26):
        bot.send_message(message.from_user.id, "Количество отображаемых отелей не должно быть"
                                               "натуральным числом, непревосходящим 25.\n"
                                               "Введите число отображаемых отелей")
        return
    with bot.retrieve_data(message.from_user.id) as data:
        data['page_size'] = int(message.text)
        hotels = hotel_list(data)
        if hotels:
            if data['sort_order'] == 'BEST_SELLER':
                filtered_hotels = []
                while float(hotels[0]['distance'].replace(',', '.').replace(' км', '')) * 1000 <= data['max_distance']:
                    for hotel in hotels:
                        if data['min_distance'] < float(hotel['distance'].replace(',', '.').replace(' км', '')) * 1000 <= \
                                data['max_distance']:
                            filtered_hotels.append(hotel)
                    if len(filtered_hotels) < int(message.text):
                        data['page'] += 1
                        hotels = hotel_list(data)
                    else:
                        break
                hotels = filtered_hotels[:int(message.text)]
            for hotel in hotels:
                exact_price = "$" + str(round(hotel["exact_price"] * data["duration"])) \
                    if hotel["exact_price"] != 0 else "Цена не указана"
                reply = f'Название: {hotel["name"]}\n' \
                        f'Адрес: {hotel["address"]}\n' \
                        f'Расстояние до центра города: {hotel["distance"]}\n' \
                        f'Цена за ночь: {hotel["price"]}\n' \
                        f'Цена за весь период: {exact_price}'
                bot.send_message(message.from_user.id, reply,
                                 reply_markup=keyboards.inline.inline_keyboard({'Показать фотографии':
                                                                                'photo' + str(hotel['id'])}))
        else:
            bot.send_message("Не удалось найти отели по данному запросу")
        req_id = set_history((message.from_user.id,
                              data['command'],
                              datetime.datetime.now().replace(microsecond=0).isoformat(sep=' '),
                              data['city']))
        set_hotels([(req_id, hotel['name'], hotel['price']) for hotel in hotels])

    bot.delete_state(message.from_user.id)


def ask_photo(call: CallbackQuery, next_state: State) -> None:
    """Функция обрабатывает запрос на отображение фотографий и отправляет приглашение ввести их количество"""
    photo_urls = get_photos_urls(call.data[5:])
    if not photo_urls:
        bot.send_message(call.from_user.id, "У этого отеля нет фотографий")
        return
    bot.set_state(call.from_user.id, next_state)
    with bot.retrieve_data(call.from_user.id) as data:
        data['photo_urls'] = photo_urls
    bot.send_message(call.from_user.id, f"Сколько фотографий загрузить? (максимум {min(len(photo_urls), 10)})")


def send_photos(message: Message) -> None:
    """Функция отправляет запрошенные фотографии"""
    if not message.text.isdigit():
        bot.send_message(message.from_user.id, "Число не распознано\nСколько фотографий вам загрузить?")
        return
    with bot.retrieve_data(message.from_user.id) as data:
        if not 0 < int(message.text) < 11:
            bot.send_message(message.from_user.id, f"Количество должно быть натуральным числом не больше"
                                                   f"{min(len(data['photo_urls']), 10)}")
            return
        bot.send_media_group(message.from_user.id, [InputMediaPhoto(data['photo_urls'][i])
                                                    for i in range(int(message.text))])
    bot.delete_state(message.from_user.id)
