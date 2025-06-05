import sqlite3

from db.db_functions import create_connection, close_connection
from config import DB_PATH


def get_recipe(recipe_id):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM recipe WHERE id = ?", (recipe_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return dict(row)
    return None


def add_recipe(
    title: str,
    image_url: str,
    calories: int,
    pfc: str,
    recipe_description: str,
    time: int,
    cost: int,
    meal: str,
    products,
):
    conn, cursor = create_connection()
    cursor.execute(
        """
    INSERT INTO recipe (title, image_url, calories, pfc, recipe_description, time, cost, meal)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """,
        (title, image_url, calories, pfc, recipe_description, time, cost, meal),
    )
    recipe_id = cursor.lastrowid
    close_connection(conn)


def get_recipes(meal):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM recipe WHERE meal = ?", (meal,))
    rows = cursor.fetchall()
    dict_recipes = [dict(row) for row in rows]
    print([dict(row) for row in rows])
    close_connection(conn)
    return dict_recipes
