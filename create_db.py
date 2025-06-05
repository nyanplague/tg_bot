import os
import sqlite3
from config import DB_PATH


def create_recipe_table(conn, cursor):
    conn.row_factory = sqlite3.Row
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS recipe (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            image_url TEXT,
            calories INT,
            pfc TEXT,
            recipe_description TEXT,
            time INT,
            cost INT,
            meal TEXT
        )
        """
    )


def create_product_table(cursor):
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS product (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE
        )
        """
    )


def create_recipe_product_table(cursor):
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS recipe_product (
            recipe_id INTEGER,
            product_id INTEGER,
            amount INTEGER,
            metric TEXT,
            PRIMARY KEY (recipe_id, product_id),
            FOREIGN KEY (recipe_id) REFERENCES recipe(id) ON DELETE CASCADE,
            FOREIGN KEY (product_id) REFERENCES product(id)
        )
        """
    )


def init_db():
    if not os.path.exists(DB_PATH):
        print("Creating db")
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        create_product_table(cursor)
        create_recipe_table(conn, cursor)
        create_recipe_product_table(cursor)

        conn.commit()
        conn.close()
        print("Db created.")
    else:
        print("Db already exists")
