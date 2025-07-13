import threading
from telebot import TeleBot, types
from datetime import date, timedelta, datetime
import time
import api

bot = TeleBot(TOKEN)

weekdays = {
    1: "Понедельник",
    2: "Вторник",
    3: "Среда",
    4: "Четверг",
    5: "Пятница",
    6: "Суббота",
    7: "Воскресенье",
}


def get_schedule_message(
    user_id: int, day: datetime.date, teacher_id: int | None = None
):
    if not teacher_id:
        group_info = api.get_user_group(int(user_id))

        if group_info is None:
            return (
                "Группа не установлена!\n\n"
                "Пожалуйста, установите свою группу с помощью команды:\n"
                "/set_group название_группы\n"
                "Пример: /set_group К1"
            )

        group_id = group_info[0]
        schedule = api.get_day_schedule(day, group_id, int(user_id))

        message_text = (
            f"Расписание на {weekdays.get(day.isoweekday())} {day}\n\n" "Занятия: \n\n"
        )

        if schedule.get("classes"):
            for i in range(len(schedule.get("classes"))):
                message_text += f"{i + 1}. {schedule.get("classes")[i]}\n\n"
        else:
            message_text += "Нет занятий в этот день\n\n"

        message_text += "\nМероприятия: \n"

        if schedule.get("events"):
            for i in range(len(schedule.get("events"))):
                message_text += f"{i + 1}. {schedule.get("events")[i]}\n\n"
        else:
            message_text += "Нет мероприятий в этот день"

    else:
        schedule = api.get_teacher_day(day, teacher_id)

        message_text = f"Расписание на {weekdays.get(day.isoweekday())} {day}:\n\n"

        if schedule:
            for i in range(len(schedule)):
                message_text += f"{i + 1}. {schedule[i]:teacher}\n\n"
        else:
            message_text += "Нет занятий в этот день\n\n"

    return message_text


def help_universal(user_id):
    message_text = (
        "Команда /today выводит занятия на текущий день.\n"
        "Команда /tomorrow - занятия на завтра.\n"
        "Команда /week - расписание на всю неделю.\n\n"
        "Команда /add название дата время - добавить событие. \n"
        "Команда /schedule - помощь в добавлении события.\n\n"
        "Команда /set_group название-группы - выбрать номер группы.\n"
        "Команда /search_teacher фамилия - поиск расписания преподавателя."
    )
    bot.send_message(user_id, message_text)


@bot.message_handler(commands=["help"])
def help_command_handler(message):
    help_universal(message.from_user.id)


@bot.callback_query_handler(func=lambda call: call.data == "help")
def help_callback_handler(call):
    help_universal(call.message.chat.id)


@bot.message_handler(commands=["start"])
def start_handler(message):
    markup = types.InlineKeyboardMarkup()
    button = types.InlineKeyboardButton("Помощь", callback_data="help")
    markup.add(button)
    bot.send_message(
        message.from_user.id,
        f'Для начала работы используйте команду "/set_group название" или нажмите на кнопку ниже!',
        reply_markup=markup,
    )


@bot.message_handler(commands=["set_group"])
def set_group_handler(message):
    try:
        group_name = message.text.split(maxsplit=1)[1].strip()
        user_id = message.from_user.id

        group_id = api.get_group_id(group_name)

        if group_id is None:
            bot.send_message(
                user_id,
                f"Группа '{group_name}' не найдена. Проверьте название и попробуйте снова.",
            )
            return

        current_group = api.get_user_group(user_id)

        if current_group:
            api.update_user_group(user_id, group_id)
            response = f"Ваша группа успешно изменена на '{group_name}'!"
        else:
            api.set_user_group(user_id, group_id)
            response = f"Группа '{group_name}' успешно установлена!"

        bot.send_message(user_id, response)

    except IndexError:
        bot.send_message(
            user_id,
            "Пожалуйста, укажите название группы после команды.\n"
            "Формат: /set_group название_группы\n"
            "Пример: /set_group К1",
        )
    except Exception as e:
        print(f"Error setting group: {e}")
        bot.send_message(
            user_id,
            "Произошла ошибка при обработке вашего запроса. Пожалуйста, попробуйте позже.",
        )


@bot.message_handler(commands=["schedule"])
def schedule_handler(message):
    message_text = (
        "Для добавления нового события используйте комманду /add в формате:\n"
        "/add название(без пробелов) дата(гггг-мм-дд) время(чч::мм)"
    )
    bot.send_message(message.from_user.id, message_text)


@bot.message_handler(commands=["add"])
def add_handler(message):
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
            reminder_date.isoformat(),
        )

        response = (
            "Событие добавлено:\n"
            f"{event}\n\n"
            "Отправлю напоминание за 24 часа до события!"
        )

    except Exception as e:
        response = (
            "Ошибка добавления события\n"
            "Формат: /add название(без пробелов) дата(гггг-мм-дд) время(чч:мм)\n"
            "Пример: /add Экзамен-Математика 2025-06-15 14:30"
        )
        print(f"Error: {e}")

    bot.send_message(message.from_user.id, response)


@bot.message_handler(commands=["today"])
def today_handler(message):
    user_id = message.from_user.id
    day = datetime.today().date()
    message_text = get_schedule_message(user_id, day)
    bot.send_message(user_id, message_text)


@bot.message_handler(commands=["tomorrow"])
def tomorrow_handler(message):
    user_id = message.from_user.id
    day = datetime.today().date() + timedelta(days=1)
    message_text = get_schedule_message(user_id, day)
    bot.send_message(user_id, message_text)


@bot.message_handler(commands=["search_teacher"])
def search_teacher_handle(message):
    try:
        teacher_name = message.text.split(maxsplit=1)[1].strip()
        user_id = message.from_user.id

        teacher_id = api.get_teacher_id(teacher_name.lower())

        if teacher_id is None:
            bot.send_message(
                user_id,
                f"Учитель с фамилией {teacher_name} не найден. Проверьте написание фамилии и попробуйте снова.",
            )
            return

        day = datetime.today().date()
        message_text = get_schedule_message(user_id, day, teacher_id)

        bot.send_message(user_id, message_text)

    except IndexError:
        bot.send_message(
            user_id,
            "Пожалуйста, укажите фамилию учителя после комманды.\n"
            "Формат: /search_teacher фамилия\n"
            "Пример: /search_teacher Иванов",
        )
    except Exception as e:
        print(f"Error setting group: {e}")
        bot.send_message(
            user_id,
            "Произошла ошибка при обработке вашего запроса. Пожалуйста, попробуйте позже.",
        )


def reminder_scheduler():
    """Background task to check and send reminders"""
    while True:
        try:
            due_reminders = api.get_due_reminders()
            for event_id, user_id, title in due_reminders:
                try:
                    bot.send_message(
                        user_id, f"🔔 Напоминание: {title}\n" "Событие скоро начнётся!"
                    )
                    api.mark_reminder_sent(event_id)
                except Exception as e:
                    print(f"Reminder failed for user {user_id}: {e}")
        except Exception as e:
            print(f"Reminder scheduler error: {e}")

        time.sleep(60)


threading.Thread(target=reminder_scheduler, daemon=True).start()

bot.polling(non_stop=True)
