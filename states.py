from aiogram.dispatcher.filters.state import State, StatesGroup


class TenantStates(StatesGroup):
    SEND_AUTH_NUMBER = State()
    ADD_USER_INFO = State()
    CAN_ADD_METERS = State()


print(TenantStates.SEND_AUTH_NUMBER.state)