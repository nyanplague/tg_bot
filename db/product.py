import sqlite3
from db.db_functions import create_connection, close_connection


def add_product(name):
    conn, cursor = create_connection()
    cursor.execute("INSERT OR IGNORE INTO product (name) VALUES (?)", (name,))
    close_connection(conn)
