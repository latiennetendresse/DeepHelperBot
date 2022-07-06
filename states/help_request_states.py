from aiogram.dispatcher.filters.state import StatesGroup, State


class Request(StatesGroup):
    Type = State()
    Description = State()
    Attachments = State()