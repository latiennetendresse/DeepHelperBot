from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

type_btn = ['Bug', 'New feature', 'Other']
btn_bug = KeyboardButton(type_btn[0])
btn_new_feature = KeyboardButton(type_btn[1])
btn_other = KeyboardButton(type_btn[2])

help_req_kb = ReplyKeyboardMarkup(resize_keyboard=True,
                                one_time_keyboard=True).add(btn_bug).add(btn_new_feature).add(btn_other)