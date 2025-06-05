import math
from copy import deepcopy

from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


class KeyboardBuilder:
    def __init__(self, buttons_text_list: list):
        self.buttons_list = buttons_text_list
        self.rows = 0
        self.buttons_keyboard = []
        self.buttons = ""
        self.reply_markup = ""

    @classmethod
    def rebuild(cls, buttons: list):
        return cls(buttons)

    def set_rows(self):
        max_buttons_in_row = 3
        buttons_amount = len(self.buttons_list)
        if buttons_amount % max_buttons_in_row == 0:
            rows = len(self.buttons_list) // 3
        if buttons_amount == max_buttons_in_row:
            rows = 1
        else:
            rows = math.ceil(buttons_amount / max_buttons_in_row)
        return rows

    def build_keyboard(self):
        self.rows = self.set_rows()
        keyboard_skeleton = []
        buttons = deepcopy(self.buttons_list)

        for row in range(self.rows):
            keyboard_skeleton.append([])
        for block in keyboard_skeleton:
            for word in buttons[:3]:
                block.append(KeyboardButton(text=word))
                buttons.remove(word)
        self.buttons = keyboard_skeleton
        self.reply_markup = ReplyKeyboardMarkup(
            keyboard=self.buttons, resize_keyboard=True
        )
        self.buttons_keyboard = keyboard_skeleton

    def delete_button(self, button_text_to_delete):
        print(self.buttons_list)
        if button_text_to_delete not in self.buttons_list:
            print("error")
        else:
            for button_text in self.buttons_list:
                if button_text_to_delete in button_text:
                    self.buttons_list.remove(button_text)
