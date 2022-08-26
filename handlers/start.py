from loader import bot


@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.from_user.id,
                     'Привет! Меня зовут Себастьян.'
                     'Я могу помочь тебе найти самый лучший для тебя отель.\n'
                     'Введи /lowprice для подборки отелей с низкой стоимостью\n'
                     'Введи /highprice для подборки отелей с высокой стоимостью проживания\n'
                     'Введи /bestdeal для подборки лучшего предложеия\n'
                     'Введи /history для вывода истории запросов\n'
                     'Введи /help" если нужна будет помощь или забудешь какую-нибудь команду,\n'
                     )


@bot.message_handler(content_types=['text'])
def non_stated(message):
    bot.send_message(message.from_user.id, "Команда не распознана. Для получения подсказок по командам введите /help")
