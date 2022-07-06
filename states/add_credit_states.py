from aiogram.dispatcher.filters.state import StatesGroup, State


class Credit(StatesGroup):
    Bank_name = State()
    Summ = State()