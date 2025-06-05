from typing import Any

from aiogram import F, types, html
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    FSInputFile,
    InputMediaPhoto,
    ReplyMarkupUnion,
    ReplyKeyboardRemove,
)

from bot import bot
from bot_commands import recipes_list_command
from general_handlers.cancel_handler import cancel
from .recipe_detailed import recipe_detailed
from .recipe_router import recipe_router
from keyboards import meals_reply_markup, build_keyboard_markup
from db.recipe import get_recipes

next_button = InlineKeyboardButton(text=">", callback_data="next")
select_button = InlineKeyboardButton(text="show recipe", callback_data="select")
previous_button = InlineKeyboardButton(text="<", callback_data="previous")

inline_keyboard_base = [[previous_button, select_button, next_button]]
inline_keyboard_without_select = [[previous_button, next_button]]


class FormShowRecipes(StatesGroup):
    meal = State()
    recipes = State()
    current_recipe = State()
    message = State()


@recipe_router.message(Command("view_recipes"))
async def view_recipes(message: Message, state: FSMContext) -> None:
    await state.clear()
    await state.set_state(FormShowRecipes.meal)
    await message.answer("Please choose meal type :", reply_markup=meals_reply_markup)


@recipe_router.message(F.text == "⬅️ return")
async def return_handler(message: Message, state: FSMContext):
    await view_recipes(message, state)


@recipe_router.message(FormShowRecipes.meal)
async def filter_recipes_by_meal(message: Message, state: FSMContext) -> None:
    data = await state.update_data(meal=message.text)
    recipes_by_meal = get_recipes(data["meal"])
    if data["meal"] == "⛔️ cancel":
        await cancel(message=message, state=state)
        return
    elif data["meal"].startswith("/"):
        await state.clear()
        await bot.send_message(
            chat_id=message.chat.id,
            text="Cancelled operation. Please choose a new command.",
            reply_markup=ReplyKeyboardRemove(),
        )
    elif len(recipes_by_meal) == 0:
        await bot.send_message(
            chat_id=message.chat.id,
            text="There is no meals available by this meal, check other pls",
            reply_markup=meals_reply_markup,
        )
    else:
        await state.set_state(FormShowRecipes.recipes)
        await state.update_data(recipes=recipes_by_meal)
        await state.set_state(FormShowRecipes.current_recipe)
        data = await state.update_data(current_recipe=0)

        main_message = await send_first_recipe(
            message=message, state=state, recipes=recipes_by_meal, data=data
        )

        await state.set_state(FormShowRecipes.message)
        await state.update_data(message=main_message)


async def send_first_recipe(message: Message, state: FSMContext, recipes, data):
    recipe = recipes[0]
    print(recipe["image_url"])
    photo_file = FSInputFile(path=recipe["image_url"])
    #
    keyboard_return_markup = build_keyboard_markup(text=["⬅️ return", data["meal"]])

    await bot.send_message(
        chat_id=message.chat.id,
        text=f"Here are your {data['meal']}s!"
        f"\nPress select to see full recipe and products needed for recipe",
        reply_markup=keyboard_return_markup,
    )

    caption = await get_caption_data(recipe)
    main_message = await bot.send_photo(
        chat_id=message.chat.id,
        caption=caption,
        photo=photo_file,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=inline_keyboard_base),
    )

    return main_message


@recipe_router.callback_query()
async def callback_query_handler(
    callback_query: types.CallbackQuery, state: FSMContext
) -> Any:
    current_recipe_id = await state.get_value("current_recipe")
    message = await state.get_value("message")
    recipes = await state.get_value("recipes")

    if callback_query.data == "next":
        await next_recipe_handler(
            callback_query, state, recipes, current_recipe_id, message
        )
    if callback_query.data == "select":
        recipes_data = await state.get_value("recipes")
        recipe_id_db = recipes_data[current_recipe_id]["id"]
        caption = recipe_detailed(recipe_id_db)
        await recipe_detailed_handler(
            callback_query, current_recipe_id, recipes, state, caption, message
        )

    if callback_query.data == "previous":
        await previous_recipe_handler(
            callback_query, state, recipes, current_recipe_id, message
        )


async def recipe_detailed_handler(
    callback_query: types.CallbackQuery,
    current_recipe_id,
    recipes,
    state: FSMContext,
    caption,
    message,
):
    await bot.edit_message_caption(
        chat_id=message.chat.id,
        message_id=message.message_id,
        caption=caption,
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=inline_keyboard_without_select
        ),
    )


async def next_recipe_handler(
    callback_query: types.CallbackQuery,
    state: FSMContext,
    recipes,
    current_recipe_id,
    message,
):
    try:
        next_recipe = recipes[current_recipe_id + 1]
    except IndexError:
        await bot.answer_callback_query(callback_query.id, text="‼️ No more recipes")
    else:
        await edit_recipe_message(message=message, recipe=next_recipe)
        await state.update_data(current_recipe=current_recipe_id + 1)


async def previous_recipe_handler(
    callback_query: types.CallbackQuery,
    state: FSMContext,
    recipes,
    current_recipe_id,
    message,
):
    previous_recipe_index = current_recipe_id - 1
    if previous_recipe_index < 0:
        pass
    else:
        previous_recipe = recipes[current_recipe_id - 1]
        await edit_recipe_message(message=message, recipe=previous_recipe)
        await state.update_data(current_recipe=current_recipe_id - 1)


async def edit_recipe_message(message, recipe):
    caption = await get_caption_data(recipe)
    photo_file = FSInputFile(path=recipe["image_url"])
    photo = InputMediaPhoto(media=photo_file)
    await bot.edit_message_media(
        chat_id=message.chat.id, message_id=message.message_id, media=photo
    )
    await bot.edit_message_caption(
        chat_id=message.chat.id,
        message_id=message.message_id,
        caption=caption,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=inline_keyboard_base),
    )


async def get_caption_data(recipe):
    recipe_title = (
        recipe["title"]
        if recipe["title"] and recipe["title"] != "None"
        else "No name meal 👍"
    )
    calories = (
        recipe["calories"]
        if recipe["calories"] and recipe["calories"] != "None"
        else "0 calories"
    )
    pfc = recipe["pfc"] if recipe["pfc"] and recipe["pfc"] != "None" else "No info"
    recipe_description = (
        recipe["recipe_description"]
        if recipe["recipe_description"] and recipe["recipe_description"] != "None"
        else "No info"
    )
    time = recipe["time"] if recipe["time"] and recipe["time"] != "None" else "No info"
    meal = recipe["meal"] if recipe["meal"] and recipe["meal"] != "None" else "No info"

    caption = (
        f"{html.bold(recipe_title)}\n\n"
        f"💪{html.bold('Calories')}: {calories}\n"
        f"🥑{html.bold('БЖУ')}: {pfc}\n"
        f"🕓{html.bold('Time')}: {time}\n"
        f"🌤{html.bold('Meal')}: {meal}"
    )

    return caption
