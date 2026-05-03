import sqlite3

def get_connection():
    return sqlite3.connect("tanka.db")

with open("./sql/init.sql") as f:
    conn = get_connection()
    cur = conn.cursor()
    cur.executescript(f.read())

def init_db():
    conn = get_connection()
    cur = conn.cursor()

    with open("./sql/init.sql") as f:
        cur.executescript(f.read())

    conn.commit()
    conn.close()

def create_event(name, start, end):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO events (name, start_date, end_date) VALUES (?, ?, ?)",
        (name, start, end)
    )

    event_id = cur.lastrowid

    conn.commit()
    conn.close()

    return event_id

def get_event_from_id(event_id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM events WHERE id = ?", (event_id,))
    event = cur.fetchone()

    conn.close()
    return event

def create_tanka(content, user_id, user_name, created_at, event_id, message_id, previous_message_id):
    conn = get_connection()
    cur = conn.cursor()

    print("INSERT......")

    cur.execute(
        "INSERT INTO tanka (content, user_id, user_name, created_at, event_id, message_id, previous_message_id) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (content, user_id, user_name, created_at, event_id, message_id, previous_message_id)
    )

    cur.execute("SELECT * FROM tanka")
    print("CHECK 短歌リスト")
    print(cur.fetchall())

    conn.commit()
    conn.close()

def get_tanka_from_message_id(message_id):
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    cur.execute("SELECT * FROM tanka WHERE message_id = ?", (message_id,))
    tanka = cur.fetchone()

    conn.close()
    return tanka