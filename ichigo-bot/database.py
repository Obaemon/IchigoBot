from datetime import datetime, timezone
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

# 歌会を作成する
def create_ichigotsumi(head_user_id, start_date, end_date):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO ichigotsumi (head_user_id, start_date, end_date) VALUES (?, ?, ?)",
        (head_user_id, start_date, end_date)
    )

    # INSERTした歌会のIDを取得
    ichigotsumi_id = cur.lastrowid

    conn.commit()
    conn.close()

    return ichigotsumi_id

# 歌会IDから歌会を検索する
def get_ichigotsumi_from_id(ichigotsumi_id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM ichigotsumi WHERE id = ?", (ichigotsumi_id,))
    ichigotsumi = cur.fetchone()

    conn.close()
    return ichigotsumi

# 投稿をデータベースに登録する
def create_post(user_id, user_name, message, post_date, ichigotsumi_id, message_id, previous_message_id):
    conn = get_connection()
    cur = conn.cursor()

    print("INSERT......")

    cur.execute(
        "INSERT INTO post (user_id, user_name, message, post_date, ichigotsumi_id, message_id, previous_message_id) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (user_id, user_name, message, post_date, ichigotsumi_id, message_id, previous_message_id)
    )

    cur.execute("SELECT * FROM post")
    print("CHECK 投稿リスト")
    print(cur.fetchall())

    conn.commit()
    conn.close()

# メッセージIDから投稿を検索する
def get_post_from_message_id(message_id):
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    cur.execute("SELECT * FROM post WHERE message_id = ?", (message_id,))
    post = cur.fetchone()

    conn.close()
    return post

# 当番リストに登録する
def set_leader(user_id, user_name):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """INSERT INTO leaders (user_id, user_name) VALUES (?, ?) 
        ON CONFLICT(user_id) DO
        UPDATE SET user_name = excluded.user_name WHERE leaders.user_name != excluded.user_name""",
        (user_id, user_name)
    )

    cur.execute("SELECT * FROM leaders")
    print("CHECK 当番リスト")
    print(cur.fetchall())

    conn.commit()
    conn.close()

# 当番リストを取得する
def get_leaders():
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    cur.execute("SELECT * FROM leaders")
    leaders = cur.fetchall()

    conn.close()
    return leaders

# 当番リストから削除する
def delete_leader(user_id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("DELETE FROM leaders WHERE user_id = ?", (user_id,))

    conn.commit()
    conn.close()
    return cur.rowcount > 0