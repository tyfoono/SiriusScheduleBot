TOKEN = "7554954438:AAEBbAjiHkkRPDDTwc9pzkw2Pn3skF1PreU"

import threading
from telebot import TeleBot, types
from datetime import date, timedelta, datetime
import time
import api

bot = TeleBot(TOKEN)


def help_universal(user_id):
    message_text = (
        "Команда /today выводит занятия на текущий день.\n"
        + "Команда /tomorrow — занятия на завтра.\n"
        + "Команда /week — расписание на всю неделю.\n"
        + "Команда /add — добавить событие. \n"
        + "Команда /schedule - помощь в добавлении события.\n"
        + "Команда /set_group - выбрать номер группы.\n"
        + "Команда /set_teacher - поиск расписания преподавателя."
    )
    bot.send_message(user_id, message_text)


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
        f"Бот, который поможет вам держать расписание под контролем! Нажмите кнопку внизу, чтобы увидеть список доступных комманд.",
        reply_markup=markup,
    )


@bot.message_handler(commands=["schedule"])
def schedule_command_handler(message):
    message_text = (
        "Для добавления нового события используйте комманду /add в формате:\n"
        "/add название(без пробелов) дата(гггг-мм-дд) время(чч::мм)"
    )
    bot.send_message(message.from_user.id, message_text)


@bot.message_handler(commands=["add"])
def add_command_handler(message):
    try:
        args = message.text.split(maxsplit=3)[1:]
        if len(args) < 3:
            raise ValueError("Invalid arguments")
        
        title = args[0]
        date_str = args[1]
        time_str = args[2]
        
        time_obj = datetime.strptime(time_str, "%H:%M").time()
        time_formatted = time_obj.strftime("%H:%M")
        
        event_date = date.fromisoformat(date_str)
        reminder_date = event_date - timedelta(days=1)
        
        event = api.add_event(
            message.from_user.id,
            title,
            date_str,
            time_formatted,
            reminder_date.isoformat()
        )
        
        response = (
            "Событие добавлено:\n"
            f"{event}\n\n"
            f"Отправлю напоминание за 24 часа до события!"
        )
        
    except Exception as e:
        response = (
            "Ошибка добавления события\n"
            "Формат: /add название(без пробелов) дата(гггг-мм-дд) время(чч:мм)\n"
            "Пример: /add Экзамен-Математика 2025-06-15 14:30"
        )
        print(f"Error: {e}")
    
    bot.send_message(message.from_user.id, response)

def reminder_scheduler():
    """Background task to check and send reminders"""
    while True:
        try:
            due_reminders = api.get_due_reminders()
            for event_id, user_id, title in due_reminders:
                try:
                    bot.send_message(
                        user_id,
                        f"🔔 Напоминание: {title}\n"
                        "Событие скоро начнётся!"
                    )
                    api.mark_reminder_sent(event_id)
                except Exception as e:
                    print(f"Reminder failed for user {user_id}: {e}")
        except Exception as e:
            print(f"Reminder scheduler error: {e}")
        
        time.sleep(60)

threading.Thread(
    target=reminder_scheduler,
    daemon=True
).start()

bot.polling(non_stop=True)
