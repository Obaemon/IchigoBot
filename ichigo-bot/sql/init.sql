CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    start_date TEXT NOT NULL,
    end_date TEXT
);

CREATE TABLE IF NOT EXISTS tanka (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    content TEXT NOT NULL,
    user_id TEXT,
    user_name TEXT,
    created_at TEXT,
    event_id INTEGER,
    message_id TEXT,
    previous_message_id TEXT,
    FOREIGN KEY (event_id) REFERENCES events(id)
);
