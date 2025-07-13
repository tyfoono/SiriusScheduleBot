import sqlite3
import datetime


def get_teacher_name(teacher_id: int) -> tuple:
    teacher_name = "Не удалось получить имя преподавателя"

    with sqlite3.connect("database.db") as con:
        cur = con.cursor()
        teacher_name = cur.execute(
            f"SELECT surname, first_name FROM teachers WHERE id = {teacher_id}"
        ).fetchone()
        con.commit()
    return teacher_name


def get_subject_name(subjects_id: int) -> str:
    subject_name = "Не удалось получить название предмета"

    with sqlite3.connect("database.db") as con:
        cur = con.cursor()
        subject_name = cur.execute(
            f"SELECT name FROM subjects WHERE id = {subjects_id}"
        ).fetchone()[0]
        con.commit()
    return subject_name


def import_class(class_id: int):
    with sqlite3.connect("database.db") as con:
        cur = con.cursor()
        row = cur.execute(
            """
            SELECT 
                c.group_id,
                c.teacher_id,
                c.subject_id,
                c.day_of_week,
                c.start_time,
                c.end_time,
                c.location
            FROM classes c
            WHERE c.id = ?
            """,
            (class_id,),
        ).fetchone()

    if not row:
        return None

    return Class(
        id=class_id,
        group_id=row[0],
        teacher=row[1],
        subject=row[2],
        day_of_week=row[3],
        start_time=datetime.datetime.strptime(row[4], "%H:%M:%S").time(),
        end_time=datetime.datetime.strptime(row[5], "%H:%M:%S").time(),
        location=row[6],
    )


class Class:
    def __init__(
        self,
        id: int,
        group_id: int,
        teacher: int,
        subject: int,
        day_of_week: int,
        start_time: datetime.time,
        end_time: datetime.time,
        location: str,
    ):
        self.id = id
        self.group = group_id
        self.teacher = teacher
        self.subject = subject
        self.day_of_week = day_of_week
        self.start_time = start_time
        self.end_time = end_time
        self.location = location

    def __str__(self):
        result = (
            f"{get_subject_name(self.subject)}\n"
            + f"{self.start_time} - {self.end_time}\n"
            + f"Преподаватель: "
            + f"{" ".join(get_teacher_name(self.teacher))}\n"
            + f"Аудитория: {self.location}"
        )

        return result


class Event:
    def __init__(
        self,
        id: int,
        user_id: int,
        title: str,
        event_date: datetime.date,
        start_time: datetime.time,
        reminder_date: datetime.date,
        reminder_sent: bool = False,
    ):
        self.id = id
        self.user_id = user_id
        self.title = title
        self.start_time = start_time
        self.event_date = event_date
        self.reminder_date = reminder_date
        self.reminder_sent = reminder_sent

    def __str__(self):
        result = f"{self.title}\n" + f"{self.event_date}, {self.start_time}"
        return result


def add_event(event):
    with sqlite3.connect() as con:
        cur = con.cursor()
        cur.execute(
            """
            INSERT INTO events 
            (user_id, title, event_date, start_time, reminder_date)
            VALUES (?, ?, ?, ?, ?)
            """,
            event.user_id,
            event.title,
            event.event_date,
            event.start_time,
            event.reminder_date,
        )
        con.commit()


def add_event(user_id, title, event_date, start_time, reminder_date):
    with sqlite3.connect("database.db") as con:
        cur = con.cursor()
        cur.execute(
            """
            INSERT INTO events 
            (user_id, title, event_date, start_time, reminder_date)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                user_id,
                title,
                event_date,
                start_time,
                reminder_date,
            ),
        )
        con.commit()
        return Event(
            cur.lastrowid, user_id, title, event_date, start_time, reminder_date
        )
