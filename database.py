import sqlite3

def init_db():
    conn = sqlite3.connect("chatbot.db")
    cursor = conn.cursor()

    # Users table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )
    """)

    # Chat history table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS chats (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        sender TEXT NOT NULL,
        message TEXT NOT NULL
    )
    """)

    # Progress tracking table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS progress (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        domain TEXT NOT NULL,
        module_id TEXT NOT NULL,
        score INTEGER DEFAULT 0,
        total INTEGER DEFAULT 0,
        accuracy REAL DEFAULT 0,
        UNIQUE(username, module_id)
    )
    """)

    conn.commit()
    conn.close()