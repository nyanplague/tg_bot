from aiogram.types import Message, ReplyKeyboardRemove


async def cancel(message: Message, state) -> None:
    await state.clear()
    await message.answer(
        "⬇️Please choose a command from the menu", reply_markup=ReplyKeyboardRemove()
    )
