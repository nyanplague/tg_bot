import sqlite3

from config import DB_PATH


def create_connection():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    return conn, cursor


def close_connection(conn):
    conn.commit()
    conn.close()


def delete_some_record(table, id):
    conn, cursor = create_connection()
    cursor.execute(f"DELETE FROM {table} WHERE id = ?", (id,))
    close_connection(conn)


def delete_some_table(table_name):
    conn, cursor = create_connection()
    cursor.execute(f"DROP TABLE {table_name}")
    close_connection(conn)
