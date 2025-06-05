import sqlite3

from config import DB_PATH
from db.db_functions import create_connection, close_connection


def get_products_by_recipe(recipe_id):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute(
        """
            SELECT 
                product.name AS product_name,
                recipe_product.amount,
                recipe_product.metric
            FROM recipe_product
            JOIN product ON recipe_product.product_id = product.id
            WHERE recipe_product.recipe_id = ?
        """,
        (recipe_id,),
    )

    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]


def create_product_recipe_relation(
    title, calories, image_url, pfc, recipe_description, time, cost, meal, products: str
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
    if not products:
        print("There is no products ")
    else:
        products_dict = products_unpack(products)
        created_products_ids = []
        for product in products_dict:
            cursor.execute(
                "INSERT OR IGNORE INTO product (name) VALUES (?)", (product["name"],)
            )
            cursor.execute("SELECT id FROM product WHERE name = ?", (product["name"],))
            product_id = cursor.fetchone()[0]
            product["id"] = product_id
            created_products_ids.append(product_id)

        for product in products_dict:
            cursor.execute(
                """
                INSERT OR REPLACE INTO recipe_product (recipe_id, product_id, amount, metric)
                VALUES (?, ?, ?, ?)
                """,
                (recipe_id, product["id"], product["amount"], product["metric"]),
            )
    close_connection(conn)


def products_unpack(products: str):
    products_data_unpack = [
        item for item in products.split("\n")
    ]  # ['хлеб 20 гр', 'Сметана 200 мл']
    products = []
    for item in products_data_unpack:
        item_info = item.split(" ")
        product_dict = {
            "name": item_info[0].lower(),
            "amount": item_info[1],
            "metric": item_info[2],
        }
        products.append(product_dict)

    return products
