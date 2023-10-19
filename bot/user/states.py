from aiogram.fsm.state import StatesGroup, State


class UserState(StatesGroup):
    new_series = State()
    add_serials = State()
    delete_serials = State()
    my_serials = State()
