from datetime import datetime, timezone
import sqlite3

def get_connection():
    return sqlite3.connect("../database/tanka.db")

def init_db():
    conn = get_connection()
    cur = conn.cursor()

    with open("./sql/init.sql", encoding="utf-8") as f:
        cur.executescript(f.read())

    conn.commit()
    conn.close()

def reload_words():
    conn = get_connection()
    cur = conn.cursor()

    with open("./sql/words.sql", encoding="utf-8") as f:
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

# 歌会開始日時から歌会を検索する
def get_ichigotsumi_from_start_date(start_date):
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    cur.execute("SELECT * FROM ichigotsumi WHERE start_date = ?", (start_date,))
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

# お題を最新からn件取得する
def get_recent_topics(n):
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    cur.execute("SELECT * FROM topics ORDER BY open_date DESC LIMIT ?", (n,))
    topics = cur.fetchall()

    conn.close()
    return topics

# 歌会IDからお題を検索する
def get_topic_from_ichigotsumi_id(ichigotsumi_id):
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    cur.execute("SELECT * FROM topics WHERE ichigotsumi_id = ?", (ichigotsumi_id,))
    topic = cur.fetchone()

    conn.close()
    return topic

# 現在受付中のお題を検索する
def get_topic_opening_now():
    now = datetime.now(timezone.utc).isoformat()

    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    cur.execute("SELECT * FROM topics WHERE open_date <= ? AND close_date >= ?", (now, now))
    topic = cur.fetchone()

    conn.close()
    return topic

def create_topic(ichigotsumi_id, open_date, close_date, leader_user_id=None):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("INSERT INTO topics (ichigotsumi_id, open_date, close_date, leader_user_id) VALUES (?, ?, ?, ?)", (ichigotsumi_id, open_date, close_date, leader_user_id))

    conn.commit()
    conn.close()

def update_topic(user_id, contents):
    now = datetime.now(timezone.utc).isoformat()

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "UPDATE topics SET contents = ? WHERE open_date <= ? AND close_date >= ? AND leader_user_id = ?",
        (contents, now, now, user_id)
    )

    conn.commit()
    conn.close()
    return cur.rowcount > 0

def get_word_list():
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    cur.execute("SELECT * FROM words")
    word_list = cur.fetchall()

    conn.close()
    return word_list