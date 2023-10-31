from aiogram.fsm.state import StatesGroup, State


class UserState(StatesGroup):
    new_series = State()
    add_serial = State()
    delete_serial = State()
    serial_info = State()
