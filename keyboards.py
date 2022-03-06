from aiogram.types import InlineKeyboardMarkup
from aiogram.types import InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData

custom_callback = CallbackData("touch", "action")

# Claim tenant invitation code button
claim_tenant_code_button = InlineKeyboardButton(
    text='Enter invitation code',
    callback_data=custom_callback.new(action='claim_tenant_code')
)
tenant_invitation_kb = InlineKeyboardMarkup()
tenant_invitation_kb.add(claim_tenant_code_button)

# Add tenant info button
add_tenant_info_button = InlineKeyboardButton(
    text='Add personal details',
    callback_data=custom_callback.new(action='add_tenant_info')
)
tenant_info_kb = InlineKeyboardMarkup()
tenant_info_kb.add(add_tenant_info_button)

# Put Meters buttons
put_meters_button = InlineKeyboardButton(text='Put meters', callback_data=custom_callback.new(action='put_meters'))
put_meters_kb = InlineKeyboardMarkup()
put_meters_kb.add(put_meters_button)


def create_buttons(list_of_elements, prefix=None, num_rows=5):
    custom_buttons_kb = InlineKeyboardMarkup(row_width=num_rows)
    string_numbers = [str(x) for x in list_of_elements]

    if prefix:
        for number in string_numbers:
            text = prefix + number
            custom_buttons_kb.add(InlineKeyboardButton(text=text, callback_data=custom_callback.new(action=text)))
    else:
        for number in string_numbers:
            custom_buttons_kb.add(InlineKeyboardButton(text=number, callback_data=custom_callback.new(action=number)))
    custom_buttons_kb.add(InlineKeyboardButton(text="Cancel", callback_data=custom_callback.new(action='cancel')))

    return custom_buttons_kb


def list_of_module_id(modules):
    module_ids = []
    for module in modules:
        module_ids.append(f"# {module['id']}")
    return module_ids


def list_of_meter_names(meters):
    meter_names = []
    for meter in meters:
        meter_names.append(meter['name'])
    return meter_names
