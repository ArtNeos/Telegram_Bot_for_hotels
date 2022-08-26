import sqlite3 as sq


def create_tables():
    """Функуия создает таблице в базе данных если их не было"""
    with sq.connect("hotels.db") as con:
        cur = con.cursor()
        cur.execute("""CREATE TABLE IF NOT EXISTS requests (
            request_id INTEGER PRIMARY KEY autoincrement,
            user_id TEXT,
            command TEXT,
            datetime TEXT,
            city TEXT);
        """)
        cur.execute("""CREATE TABLE IF NOT EXISTS hotels(
               id INTEGER PRIMARY KEY autoincrement,
               request_id INTEGER,
               name TEXT,
               price INTEGER);
        """)


def set_history(history: list) -> int:
    """Сохраняет в базу данных запись о запросе и возвращает rowid созданной записи"""
    with sq.connect("hotels.db") as con:
        cur = con.cursor()
        cur.execute("INSERT INTO requests VALUES (NULL, ?, ?, ?, ?)", history)
        cur.execute("SELECT last_insert_rowid()")
        res = cur.fetchone()
        return res[0]


def get_history(user_id: int):
    """Возвращает записи о запросах пользователя с данным id"""
    with sq.connect("hotels.db") as con:
        cur = con.cursor()
        cur.execute(f"SELECT request_id, command, datetime, city FROM requests WHERE user_id={user_id}")
        return cur.fetchall()


def set_hotels(hotels: list):
    """Сохраняет в базу данных записи об отелях"""
    with sq.connect("hotels.db") as con:
        cur = con.cursor()
        cur.executemany("INSERT INTO hotels VALUES (NULL, ?, ?, ?)", hotels)


def get_hotels(request_id: int):
    """Возвращает записи об отелях из запроса с заданным id"""
    with sq.connect("hotels.db") as con:
        cur = con.cursor()
        cur.execute(f"SELECT name, price FROM hotels WHERE request_id={request_id}")
        return cur.fetchall()
