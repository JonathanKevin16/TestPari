import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

DB_NAME = 'inventory.db'


def connect_db():
    conn = sqlite3.connect(DB_NAME, timeout=5)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode=WAL")
    print(f"Connected to database: {DB_NAME}")
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


class User:
    def __init__(self, username, password):
        self.username = username
        self.password = generate_password_hash(password)

    def save(self):
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO User (username, password) VALUES (?, ?)", (self.username, self.password))
        conn.commit()
        conn.close()

    @staticmethod
    def find_by_username(username):
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM User WHERE username = ?", (username,))
        user = cursor.fetchone()
        conn.close()
        return user

    @staticmethod
    def check_password(stored_password_hash, password):
        return check_password_hash(stored_password_hash, password)

    def authenticate(username, password):
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT password FROM User WHERE username = ?", (username,))
        user = cursor.fetchone()
        conn.close()

        if user and check_password_hash(user[0], password):
            return True
        return False
