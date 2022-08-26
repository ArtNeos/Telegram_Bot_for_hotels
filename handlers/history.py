from loader import bot
from database.database_handler import get_history, get_hotels


@bot.message_handler(commands=['history'])
def history(message):
    user_history = get_history(message.from_user.id)
    if user_history:
        reply = "Ваши запросы:\n\n"
        for record in user_history:
            record_id = record[0]
            hotels = get_hotels(record_id)
            reply += f"Дата и время {record[2]}\n" \
                     f"Команда: {record[1]}\n" \
                     f"Город запроса: {record[3]}\n"

            if hotels:
                reply += "Найденные отели:\n"
                for i in range(len(hotels)):
                    reply += f"    {i+1}. {hotels[i][0]} ({hotels[i][1]})\n"
            else:
                reply += "Отели найдены не были\n"
            reply += "\n\n"
    else:
        reply = "Ваша история пуста"
    bot.send_message(message.from_user.id, reply)
