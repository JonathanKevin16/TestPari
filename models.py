import sqlite3
from datetime import datetime

DB_NAME = 'inventory.db'


def connect_db():
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    with open('database_setup.sql') as f:
        conn = connect_db()
        conn.executescript(f.read())
        conn.commit()
        conn.close()


class Category:
    def __init__(self, name):
        self.name = name

    def save(self):
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO Category (name) VALUES (?)", (self.name,))
        conn.commit()
        conn.close()


class Item:
    def __init__(self, category_id, name, description, price):
        self.category_id = category_id
        self.name = name
        self.description = description
        self.price = price
        self.created_at = datetime.now()

    def save(self):
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO Item (category_id, name, description, price, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, (self.category_id, self.name, self.description, self.price, self.created_at))
        conn.commit()
        conn.close()
