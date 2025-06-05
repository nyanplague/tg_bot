from aiogram.types import BotCommand

start_command = BotCommand(command="/start", description="Press to start")
recipes_list_command = BotCommand(
    command="/view_recipes", description="View list of recipes"
)
add_recipe_command = BotCommand(command="add_recipe", description="Add a new recipe")
