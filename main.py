import os

TOKEN = os.getenv("TOKEN")

from telebot import TeleBot, types

bot = TeleBot(TOKEN)

def help_universal(user_id):
    message_text = "Команда /today выводит занятия на текущий день.\n" + \
                "Команда /tomorrow — занятия на завтра.\n" + \
                "Команда /week — расписание на всю неделю.\n" + \
                "Команда /add — добавить событие."

    markup = types.InlineKeyboardMarkup()

    bot.send_message(
        user_id,
        message_text
    )

@bot.message_handler(commands=["help"])
def help_command_handler(message):
    help_universal(message.from_user.id)

@bot.callback_query_handler(func=lambda call: call.data == "help")
def help_callback_handler(call):
    help_universal(call.message.chat.id)

@bot.message_handler(commands=["start"])
def start_command_handler(message):
    markup = types.InlineKeyboardMarkup()
    button = types.InlineKeyboardButton("Помощь", callback_data="help")
    markup.add(button)
    bot.send_message(
        message.from_user.id,
        "Бот, который поможет вам держать расписание под контролем! Нажмите кнопку внизу, чтобы увидеть список доступных комманд.",
        reply_markup=markup
    )

@bot.message_handler(commands=["schedule"])
def schedule_command_handler(message):
    message_text = "Для добавления нового события используйте комманду /add в формате:\n" \
                "/add название-события дд-мм-гггг чч::мм"
    bot.send_message(message.from_user.id, message_text)

bot.polling()
