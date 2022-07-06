from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData

level_0_kb=InlineKeyboardMarkup(row_width=1).add(InlineKeyboardButton(text="Работа с кредитами", callback_data="credit"),
                                      InlineKeyboardButton(text="Запрос в службу поддержки", callback_data="request"))

level_1_kb=InlineKeyboardMarkup(row_width=1).add(
                    InlineKeyboardButton(text="Добавить данные о новом кредите", callback_data="add_credit"),
                    InlineKeyboardButton(text="Рассчитать кредитный пакет в процентах", callback_data="calculate"),
                    InlineKeyboardButton(text="Назад", callback_data="to_lvl_0"))

