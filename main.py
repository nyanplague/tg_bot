import asyncio
import logging
import sys
from aiogram import Dispatcher, html, F
from aiogram.filters import CommandStart, Command
from aiogram.types import (
    Message,
    MenuButton,
    MenuButtonCommands,
    ReplyKeyboardRemove,
)
from bot import bot
from recipe_handlers import get_recipes
from recipe_handlers import add_recipe
from bot_commands import (
    start_command,
    recipes_list_command,
    add_recipe_command,
)
from recipe_handlers.recipe_router import recipe_router
from create_db import init_db


dp = Dispatcher()


menu = MenuButton(type="default")


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    await message.answer(
        f"Hello, {html.bold(message.from_user.full_name)}!\n"
        f"This bot can help you manage your recipes.\n"
        f"Click the menu button to find command.\n\n"
        f"/add_recipe to create recipe\n"
        f"/view_recipes to see the full list of your recipes",
        reply_markup=ReplyKeyboardRemove(),
    )


async def main() -> None:
    init_db()
    dp.include_router(recipe_router)
    await bot.set_my_commands([start_command, recipes_list_command, add_recipe_command])
    await dp.start_polling(bot)
    menu_button = MenuButtonCommands()
    await bot.set_chat_menu_button(menu_button=menu_button)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
