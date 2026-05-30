CREATE TABLE IF NOT EXISTS ichigotsumi (
    id INTEGER PRIMARY KEY,
    head_user_id TEXT NOT NULL,
    start_date TEXT NOT NULL,
    end_date TEXT
);

CREATE TABLE IF NOT EXISTS post (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    user_name TEXT NOT NULL,
    message TEXT NOT NULL,
    post_date TEXT NOT NULL,
    ichigotsumi_id INTEGER NOT NULL,
    message_id TEXT NOT NULL,
    previous_message_id TEXT,
    FOREIGN KEY (ichigotsumi_id) REFERENCES ichigotsumi(id)
);

CREATE TABLE IF NOT EXISTS leaders (
    user_id TEXT PRIMARY KEY,
    user_name TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS topics (
    ichigotsumi_id INTEGER NOT NULL,
    open_date TEXT NOT NULL,
    close_date TEXT NOT NULL,
    leader_user_id TEXT,
    contents TEXT
);

CREATE TABLE IF NOT EXISTS words (
    word TEXT NOT NULL,
    season INTEGER,
    month INTEGER
);
