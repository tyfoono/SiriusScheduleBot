import sqlite3
import datetime


def get_teacher_name(teacher_id: int) -> tuple:
    teacher_name = "Не удалось получить имя преподавателя"

    with sqlite3.connect("database.db") as con:
        cur = con.cursor()
        teacher_name = cur.execute(
            f"SELECT surname, first_name FROM teachers WHERE id = {teacher_id}"
        ).fetchone()

    return teacher_name


def get_subject_name(subjects_id: int) -> str:
    subject_name = "Не удалось получить название предмета"

    with sqlite3.connect("database.db") as con:
        cur = con.cursor()
        subject_name = cur.execute(
            f"SELECT name FROM subjects WHERE id = {subjects_id}"
        ).fetchone()[0]

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
        title: str,
        event_date: datetime.date,
        start_time: datetime.time,
        location: str,
        reminder_date: datetime.date,
        reminder_time: datetime.time,
    ):
        self.id = id
        self.title = title
        self.start_time = start_time
        self.location = location
        self.event_date = event_date
        self.reminder_date = reminder_date
        self.reminder_time = reminder_time

    def __str__(self):
        result = ""
        return result


def add_event(event):
    with sqlite3.connect() as con:
        cur = con.cursor()
        cur.execute(
            """
            INSERT INTO events 
            (title, event_date, start_time, location, reminder_date, reminder_time)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            event.title,
            event.event_date,
            event.start_time,
            event.location,
            event.reminder_date,
            event.reminder_time,
        )
