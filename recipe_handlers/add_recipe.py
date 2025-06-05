from typing import Any
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.fsm.state import StatesGroup, State

from db.recipe_product import create_product_recipe_relation
from keyboards import (
    skip_cancel_keyboard,
    confirmation_recipe_keyboard,
    meals_reply_markup,
    preparing_time_keyboard,
)
from db.recipe import add_recipe
from bot import bot
from general_handlers.cancel_handler import cancel
from .get_recipes import view_recipes
from .recipe_router import recipe_router
from aiogram import Dispatcher, html, F
from bot_commands import add_recipe_command
from config import IMAGES_DIR

TOKEN = "7366455972:AAHizUa6fwkzYilhHBooeNrpsX2EhVr_41I"


class FormRecipe(StatesGroup):
    title = State()
    image_url = State()
    calories = State()
    pfc = State()
    recipe_description = State()
    time = State()
    cost = State()
    meal = State()
    confirm = State()
    products = State()


@recipe_router.message(Command("add_recipe"))
async def add_recipe(message: Message, state: FSMContext) -> None:
    await state.clear()
    await state.set_state(FormRecipe.title)
    await message.answer(
        "Hi, what's the title of recipe? It should be unique",
        reply_markup=skip_cancel_keyboard,
    )


async def _handle_skip(
    state: FSMContext,
    message: Message,
    field_name: str,
    default_value: Any | None = None,
):
    if message.text == "skip":
        await state.update_data(**{field_name: default_value})
        return True
    elif message.text and message.text.startswith("/"):
        await state.clear()
        await bot.send_message(
            chat_id=message.chat.id,
            text="Cancelled operation. Please choose a new command.",
            reply_markup=ReplyKeyboardRemove(),
        )

    elif message.text == "⛔️ cancel":
        await cancel(message, state)
        return False
    else:
        if field_name == "image_url":
            await state.update_data(**{field_name: message})
        else:
            await state.update_data(**{field_name: message.text})
        return True


@recipe_router.message(FormRecipe.title)
async def process_title(message: Message, state: FSMContext) -> None:
    if await _handle_skip(state, message, "title"):
        await state.set_state(FormRecipe.image_url)
        await message.answer(
            f"Thank you! Send me a photo", reply_markup=skip_cancel_keyboard
        )


@recipe_router.message(FormRecipe.image_url)
async def process_image_url(message: Message, state: FSMContext) -> None:
    if await _handle_skip(state, message, "image_url"):
        await state.set_state(FormRecipe.calories)
        await message.answer(
            f"How many calories are there?", reply_markup=skip_cancel_keyboard
        )


@recipe_router.message(FormRecipe.calories)
async def process_calories(message: Message, state: FSMContext) -> None:
    if await _handle_skip(state, message, "calories"):
        await state.set_state(FormRecipe.pfc)
        await message.answer(f"Protein/fat/carbs?", reply_markup=skip_cancel_keyboard)


@recipe_router.message(FormRecipe.pfc)
async def process_pfc(message: Message, state: FSMContext) -> None:
    if await _handle_skip(state, message, "pfc"):
        await state.set_state(FormRecipe.recipe_description)
        await message.answer(
            f"Detailed description how to cook?", reply_markup=skip_cancel_keyboard
        )


@recipe_router.message(FormRecipe.recipe_description)
async def process_recipe_description(message: Message, state: FSMContext) -> None:
    if await _handle_skip(state, message, "recipe_description"):
        await state.set_state(FormRecipe.products)
        example = html.bold("малина 2 шт\nмолоко 200 мл\nгречка 20 гр")
        await message.answer(
            f"""Send products list separate by enter, adding amount and metric\n\n{example}\n\n⚠️Metrics to use: шт, мл, л, гр""",
            reply_markup=skip_cancel_keyboard,
        )


@recipe_router.message(FormRecipe.products)
async def process_products(message: Message, state: FSMContext) -> None:
    if await _handle_skip(state, message, "products"):
        await state.set_state(FormRecipe.time)
        data = await state.get_data()
        print(data["products"])
        await message.answer(
            f"How long does it take to cook?", reply_markup=preparing_time_keyboard
        )


@recipe_router.message(FormRecipe.time)
async def process_time(message: Message, state: FSMContext) -> None:
    if await _handle_skip(state, message, "time"):
        await state.set_state(FormRecipe.cost)
        await message.answer(
            f"How much does it cost?", reply_markup=skip_cancel_keyboard
        )


@recipe_router.message(FormRecipe.cost)
async def process_cost(message: Message, state: FSMContext) -> None:
    if await _handle_skip(state, message, "cost"):
        await state.set_state(FormRecipe.meal)
        await message.answer(f"Choose meal type", reply_markup=meals_reply_markup)


@recipe_router.message(FormRecipe.meal)
async def process_meal(message: Message, state: FSMContext) -> None:
    if message.text == "cancel":
        await state.clear()
        await message.answer(
            "Hello, here we start again",
        )

    else:
        if message.text == "skip":
            data = await state.update_data(meal=None)
        else:
            data = await state.update_data(meal=message.text)
        print(data.items())
        (
            title,
            image_url,
            calories,
            pfc,
            recipe_description,
            time,
            cost,
            meal,
            products,
        ) = data.items()
        await state.set_state(FormRecipe.confirm)
        caption = await create_caption_data(
            title, calories, pfc, recipe_description, time, cost, meal, products
        )

        await message.answer(
            f"""This is data you have provided:\n{caption} \nPlease confirm or cancel""",
            reply_markup=confirmation_recipe_keyboard,
        )


@recipe_router.message(FormRecipe.confirm)
async def process_confirmation(message: Message, state: FSMContext) -> None:
    if message.text == "confirm":
        data = await state.update_data(confirm="ok")
        await process_recipe(data)
        await message.answer(
            text="A new recipe was added! thanks", reply_markup=ReplyKeyboardRemove()
        )

        message_with_photo = data["image_url"]

        await state.clear()


async def process_recipe(data):
    if not data["image_url"] or data["image_url"] == "None":
        print("NO PHOTO")
        image_url = f"{IMAGES_DIR}/no_img.png"
    else:
        message_with_photo = data["image_url"]
        file_id = message_with_photo.photo[-1].file_id
        file = await bot.get_file(file_id)
        file_path = file.file_path
        await bot.download_file(file_path, f"{IMAGES_DIR}/{file_id}.jpg")
        image_url = f"{IMAGES_DIR}/{file_id}.jpg"

    create_product_recipe_relation(
        title=data["title"],
        image_url=image_url,
        calories=data["calories"],
        pfc=data["pfc"],
        recipe_description=data["recipe_description"],
        time=data["time"],
        cost=data["cost"],
        meal=data["meal"],
        products=data["products"],
    )


async def create_caption_data(
    title, calories, pfc, recipe_description, time, cost, meal, products
):
    recipe_title = title[1] if title[1] and title[1] != "None" else "No name meal 👍"
    calories = calories[1] if calories[1] and calories[1] != "None" else "0 calories"
    pfc = pfc[1] if pfc[1] and pfc[1] != "None" else "No info"
    recipe_description = (
        recipe_description[1]
        if recipe_description[1] and recipe_description[1] != "None"
        else "No info"
    )
    time = time[1] if time[1] and time[1] != "None" else "No info"
    meal = meal[1] if meal[1] and meal[1] != "None" else "No info"

    caption = (
        f"{html.bold(recipe_title)}\n\n"
        f"💪{html.bold('Calories')}: {calories}\n"
        f"🥑{html.bold('БЖУ')}: {pfc}\n"
        f"🕓{html.bold('Time')}: {time}\n"
        f"🌤{html.bold('Meal')}: {meal}"
    )

    return caption
