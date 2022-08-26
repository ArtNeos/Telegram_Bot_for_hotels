from loader import bot


@bot.message_handler(commands=['help'])
def help_command(message):
    bot.send_message(message.from_user.id,
                     'Введи /lowprice для подборки отелей с низкой ценой за ночь\n'
                     'Введи /highprice для подборки отелей с высокой ценой за ночь\n'
                     'Введи /bestdeal для подборки лучшего предложеия\n'
                     'Введи /history для вывода истории запросов\n'
                     )
