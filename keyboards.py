from keyboard_builder import KeyboardBuilder


def build_keyboard_markup(text: list):
    builder = KeyboardBuilder(buttons_text_list=text)
    builder.build_keyboard()
    return builder.reply_markup


meals_reply_markup = build_keyboard_markup(
    [
        "🍳 breakfast",
        "🥗 lunch",
        "🍝 dinner",
        "☕ drinks",
        "🍭 fancy stuff",
        "⛔️ cancel",
    ]
)
# "🔍 search by title"
skip_cancel_keyboard = build_keyboard_markup(["skip", "⛔️ cancel"])
confirmation_recipe_keyboard = build_keyboard_markup(["confirm", "⛔️ cancel"])
preparing_time_keyboard = build_keyboard_markup(["15 min", "30 min", "1h", "2h+"])
