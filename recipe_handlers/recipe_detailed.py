from db.recipe import get_recipe
from aiogram import html

from db.recipe_product import get_products_by_recipe


def recipe_detailed(
    recipe_id,
):
    recipe_data = get_recipe(recipe_id)
    products_data = get_products_by_recipe(recipe_id)
    caption = create_caption(recipe_data, products_data)
    return caption


def create_caption(recipe_data, product_data):
    product_string = ""
    print(type(product_data))
    if product_data:
        print("HERE ARE PRODUCT DATA", product_data)
        for product in product_data:
            print(product["product_name"])
            product_string += f"""{product['product_name']} {str(product["amount"])} {product["metric"]}\n"""
    else:
        product_string = "Sorry it wasn't provided"

    caption = (
        f"{html.bold(recipe_data['title'])}\n\n"
        f"💪{html.bold('Calories')}: {recipe_data['calories']}\n"
        f"🥑{html.bold('БЖУ')}: {recipe_data['pfc']}\n"
        f"🕓{html.bold('Time')}: {recipe_data['time']}\n"
        f"🌤{html.bold('Meal')}: {recipe_data['meal']}\n"
        f"📕{html.bold('Recipe')}: {recipe_data['recipe_description']}\n\n"
        f"🍶{html.bold('Products')}:\n"
        f"{product_string}"
    )
    return caption
