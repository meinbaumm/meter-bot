import re

import logging
from aiogram.contrib.fsm_storage.redis import RedisStorage2
from aiogram.dispatcher import FSMContext

from aiogram import Bot, types
from aiogram.types import BotCommand
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiogram.utils.markdown import text
from aiogram.types import ParseMode
from aiogram.types.message import ContentType
from aiogram.utils.emoji import emojize

from config import BOT_TOKEN, BOT_AUTH_PARAMS
from config import REDIS_HOST, REDIS_PORT, REDIS_DB, REDIS_POOL_SIZE, REDIS_PREFIX

import backend_requests as br
import messages as msg
import keyboards
import support_functions

from states import TenantStates

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
storage = RedisStorage2(
    host=REDIS_HOST,
    port=REDIS_PORT,
    db=REDIS_DB,
    pool_size=REDIS_POOL_SIZE,
    prefix=REDIS_PREFIX
)
dp = Dispatcher(bot, storage=storage)

GLOBAL_USER_VARS = {}


async def set_commands(bot: Bot):
    commands = [
        BotCommand(command="/start", description="Getting Started"),
        BotCommand(command="/put_meters", description="Put meters"),
        BotCommand(command="/info", description="Instructions for using the bot"),
        BotCommand(command="/contacts", description="Contacts"),
    ]
    await bot.set_my_commands(commands)


async def shutdown(dispatcher: Dispatcher):
    await dispatcher.storage.close()
    await dispatcher.storage.wait_closed()


# COMMANDS


@dp.message_handler(commands=['start'], state='*')
async def process_start_command(message: types.Message, state: FSMContext):
    await set_commands(bot)
    current_state = await state.get_state()
    logging.info('Current state is %r', current_state)

    if current_state is None:
        GLOBAL_USER_VARS[str(message.from_user.id)] = {}
        message_info_text = text(emojize(msg.intro))
        message_claim_code = text(emojize(msg.claim_code))

        await message.reply(message_info_text, parse_mode=ParseMode.MARKDOWN, reply=False)
        await message.reply(
            message_claim_code,
            reply_markup=keyboards.tenant_invitation_kb,
            parse_mode=ParseMode.MARKDOWN,
            reply=False
        )
        await TenantStates.SEND_AUTH_NUMBER.set()

        logging.info('Current state is %r', current_state)

    elif current_state == TenantStates().SEND_AUTH_NUMBER.state:
        await message.reply(
            msg.put_claim_code,
            reply_markup=keyboards.tenant_invitation_kb,
            parse_mode=ParseMode.MARKDOWN,
            reply=False
        )

        logging.info('Current state is %r', current_state)

    elif current_state == TenantStates().ADD_USER_INFO.state:
        await message.reply(
            msg.need_add_tenant_info,
            reply_markup=keyboards.tenant_info_kb,
            parse_mode=ParseMode.MARKDOWN,
            reply=False
        )

        logging.info('Current state is %r', current_state)

    elif current_state == TenantStates().CAN_ADD_METERS.state:
        await message.reply(
            msg.can_put_meters,
            reply_markup=keyboards.put_meters_kb,
            parse_mode=ParseMode.MARKDOWN,
            reply=False
        )

        logging.info('Current state is %r', current_state)


@dp.message_handler(commands=['info'], state='*')
async def process_help_command(message: types.Message, state: FSMContext):
    message_text = text(emojize(msg.info))
    current_state = await state.get_state()
    logging.info('Current state is %r', current_state)
    if current_state != TenantStates().CAN_ADD_METERS.state:
        await message.reply(message_text, parse_mode=ParseMode.MARKDOWN, reply=False)
    else:
        await message.reply(
            message_text,
            reply_markup=keyboards.put_meters_kb,
            parse_mode=ParseMode.MARKDOWN,
            reply=False
        )


@dp.message_handler(commands=['contacts'], state='*')
async def process_help_command(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    logging.info('Current state is %r', current_state)
    if current_state != TenantStates().CAN_ADD_METERS.state:
        await message.reply(msg.contacts, parse_mode=ParseMode.MARKDOWN, reply=False)
    else:
        await message.reply(
            msg.contacts,
            reply_markup=keyboards.put_meters_kb,
            parse_mode=ParseMode.MARKDOWN,
            reply=False
        )


@dp.message_handler(commands=['put_meters'], state='*')
async def process_help_command(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    logging.info('Current state is %r', current_state)
    if current_state == TenantStates().SEND_AUTH_NUMBER.state:
        await message.reply(
            msg.put_claim_code,
            reply_markup=keyboards.tenant_invitation_kb,
            parse_mode=ParseMode.MARKDOWN,
            reply=False
        )
        logging.info('Current state is %r', current_state)
    elif current_state == TenantStates().ADD_USER_INFO.state:
        await message.reply(
            msg.need_add_tenant_info,
            reply_markup=keyboards.tenant_info_kb,
            parse_mode=ParseMode.MARKDOWN,
            reply=False
        )
        logging.info('Current state is %r', current_state)
    elif current_state == TenantStates().CAN_ADD_METERS.state:
        await message.reply(
            msg.can_put_meters,
            reply_markup=keyboards.put_meters_kb,
            parse_mode=ParseMode.MARKDOWN,
            reply=False
        )


# BUTTONS AND ACTIONS

@dp.callback_query_handler(
    keyboards.custom_callback.filter(action=["claim_tenant_code"]),
    state="*"
)
async def put_invitation_code(call: types.CallbackQuery, state: FSMContext):
    info = {
        "telegram_id": str(call.from_user.id),
    }
    current_state = await state.get_state()
    logging.info('Current state is %r', current_state)
    if current_state == TenantStates().SEND_AUTH_NUMBER.state:
        await call.message.reply(msg.put_claim_code, parse_mode=ParseMode.MARKDOWN)

        @dp.message_handler(state=TenantStates.SEND_AUTH_NUMBER)
        async def get_message_from_user(message: types.Message):
            try:
                user_input_code = int(message.text)
            except:
                await call.message.reply(msg.only_int_values_required)
                await call.message.reply(msg.put_claim_code, parse_mode=ParseMode.MARKDOWN)

            claim_invitation_code_response = br.claim_invitation_code(user_input_code, info['telegram_id'], TOKEN)
            if claim_invitation_code_response == 200:
                await message.reply(
                    msg.new_tenant_successfully_created,
                    parse_mode=ParseMode.MARKDOWN,
                    reply_markup=keyboards.tenant_info_kb,
                    reply=False
                )
                await TenantStates.ADD_USER_INFO.set()
                logging.info('Current state is %r', current_state)
            elif claim_invitation_code_response == 422:
                await message.reply(
                    msg.tenant_already_exist,
                    parse_mode=ParseMode.MARKDOWN,
                    reply_markup=keyboards.put_meters_kb,
                    reply=False
                )
                await TenantStates.CAN_ADD_METERS.set()
                logging.info('Current state is %r', current_state)
            else:
                await message.reply(
                    msg.try_put_invitation_code_again,
                    reply_markup=keyboards.tenant_invitation_kb,
                    reply=False
                )
                logging.info('Current state is %r', current_state)
    else:
        await call.message.reply(msg.code_already_claimed, parse_mode=ParseMode.MARKDOWN)
        logging.info('Current state is %r', current_state)


@dp.callback_query_handler(
    keyboards.custom_callback.filter(action=["add_tenant_info"]),
    state=TenantStates.ADD_USER_INFO
)
async def adding_tenant_info(call: types.CallbackQuery, state: FSMContext):
    info = {
        "telegram_id": str(call.from_user.id),
    }
    current_state = await state.get_state()
    logging.info('Current state is %r', current_state)
    message_text = text(emojize(msg.need_add_tenant_info))
    await call.message.reply(message_text, reply_markup=keyboards.add_tenant_info_button, parse_mode=ParseMode.MARKDOWN)

    @dp.message_handler(state=TenantStates.ADD_USER_INFO)
    async def get_message_from_user(message: types.Message):
        user_input = message.text.split(" ")
        last_name = user_input[0]
        first_name = user_input[1]
        patronymic = user_input[2]
        prettify_response, _ = br.update_tenant(info["telegram_id"], first_name, last_name, patronymic, TOKEN)
        await message.reply(f"I've recorded\n\n{prettify_response}", parse_mode=ParseMode.MARKDOWN)
        await message.reply(msg.tenant_info_successfully_added, reply_markup=keyboards.put_meters_kb)
        await TenantStates.CAN_ADD_METERS.set()
        logging.info('Current state is %r', current_state)


@dp.callback_query_handler(keyboards.custom_callback.filter(action=["put_meters"]), state=TenantStates.CAN_ADD_METERS)
async def get_modules(call: types.CallbackQuery):
    info = {
        "telegram_id": call.from_user.id,
        "first_name": call.from_user.first_name,
        "last_name": call.from_user.last_name,
        "username": call.from_user.username
    }
    tenant_authorised = br.check_tenant_auth(info["telegram_id"], TOKEN)

    # Authorisation
    if tenant_authorised:
        prettify_response, body = br.list_tenant_modules(info['telegram_id'], TOKEN)
        list_module_keys = keyboards.list_of_module_id(body)
        GLOBAL_USER_VARS[str(call.from_user.id)]['dict_modules'] = support_functions.create_dict_from_two_lists(
            list_module_keys, body)

        module_buttons = keyboards.create_buttons(
            list(GLOBAL_USER_VARS[str(call.from_user.id)]['dict_modules'].keys()),
            num_rows=5,
            prefix='Module '
        )
        await call.message.reply(
            prettify_response,
            reply_markup=module_buttons,
            parse_mode=ParseMode.MARKDOWN,
            reply=False
        )
    else:
        message_text = text(emojize(msg.error))
        await call.message.reply(
            message_text,
            reply_markup=keyboards.put_meters_kb,
            parse_mode=ParseMode.MARKDOWN,
            reply=False
        )


@dp.callback_query_handler(lambda c: c.data.split(':')[1].startswith('Module'), state=TenantStates.CAN_ADD_METERS)
async def get_meters(call: types.CallbackQuery):
    info = {
        "telegram_id": call.from_user.id,
        "first_name": call.from_user.first_name,
        "last_name": call.from_user.last_name,
        "username": call.from_user.username
    }
    action = call.data
    owner_property = re.search("\#(..)", action)
    property_number = owner_property.group(0)

    if property_number in GLOBAL_USER_VARS[str(call.from_user.id)]['dict_modules'].keys():
        await call.message.reply(f"You have selected a module {property_number}")
        chosen_property = GLOBAL_USER_VARS[str(call.from_user.id)]['dict_modules'][property_number]
        # Pass id of chosen module into global variable
        GLOBAL_USER_VARS[str(call.from_user.id)]['property_id'] = \
            GLOBAL_USER_VARS[str(call.from_user.id)]['dict_modules'][property_number]['id']
        prettify, body = br.list_module_meters(property_id=chosen_property['id'], token=TOKEN)

        list_meter_names = keyboards.list_of_meter_names(body)
        GLOBAL_USER_VARS[str(call.from_user.id)]['dict_meters'] = support_functions.create_dict_from_two_lists(
            list_meter_names, body)

        meters_buttons = keyboards.create_buttons(list_meter_names, num_rows=1, prefix='Meter ')
        meters_buttons.add(
            types.InlineKeyboardButton(
                text="To module selection",
                callback_data=keyboards.custom_callback.new(action='back_to_modules')
            )
        )
        GLOBAL_USER_VARS[str(call.from_user.id)]['meter_buttons'] = meters_buttons
        await call.message.reply(
            prettify,
            reply_markup=meters_buttons,
            parse_mode=ParseMode.MARKDOWN,
            reply=False
        )
    else:
        message_text = text(emojize(msg.error))
        await call.message.reply(
            message_text,
            reply_markup=keyboards.put_meters_kb,
            parse_mode=ParseMode.MARKDOWN,
            reply=False
        )


@dp.callback_query_handler(lambda c: c.data.split(':')[1].startswith('Meter'), state=TenantStates.CAN_ADD_METERS)
async def get_meters(call: types.CallbackQuery):
    info = {
        "telegram_id": call.from_user.id,
        "first_name": call.from_user.first_name,
        "last_name": call.from_user.last_name,
        "username": call.from_user.username
    }
    action = call.data
    name = re.search("(?<=Счетчик ).*$", action)
    meter_name = name.group(0)
    GLOBAL_USER_VARS[str(call.from_user.id)]["dict_meters"]["chosen_meter"] = meter_name
    if meter_name in GLOBAL_USER_VARS[str(call.from_user.id)]['dict_meters'].keys():
        message_text = text(emojize(f"You have selected a meter {meter_name}\n\n"
                                    f"Enter the *integer* you want to pass for this meter\n"
                                    "You do not need to enter zeros in front of the number :flexed_biceps:"))
        await call.message.reply(message_text, parse_mode=ParseMode.MARKDOWN, reply=False)

        # Pass id of chosen meter into global variable
        GLOBAL_USER_VARS[str(call.from_user.id)]['meter_id'] = \
            GLOBAL_USER_VARS[str(call.from_user.id)]['dict_meters'][meter_name]['id']

    @dp.message_handler(lambda message: message.text, state=TenantStates.CAN_ADD_METERS)
    async def get_message_from_user(message: types.Message):

        user_input = support_functions.handle_user_meter_input(message.text)

        new_transaction = br.create_meter_transaction(
            property_id=GLOBAL_USER_VARS[str(message.from_user.id)]['property_id'],
            meter_id=GLOBAL_USER_VARS[str(message.from_user.id)]['meter_id'],
            value=user_input,
            token=TOKEN
        )

        if new_transaction == 200:
            name_of_meter = GLOBAL_USER_VARS[str(call.from_user.id)]["dict_meters"]["chosen_meter"]
            await message.reply(
                f"I've recorded for the counter *{name_of_meter}* the reading *{user_input}*",
                reply_markup=GLOBAL_USER_VARS[str(call.from_user.id)]['meter_buttons'],
                parse_mode=ParseMode.MARKDOWN,
                reply=False
            )
        elif new_transaction == 422:
            name_of_meter = GLOBAL_USER_VARS[str(call.from_user.id)]["dict_meters"]["chosen_meter"]
            await message.reply(
                text(emojize(f'This month for the meter *{name_of_meter}* the readings are transferred :heavy_check_mark:')),
                reply_markup=GLOBAL_USER_VARS[str(call.from_user.id)]['meter_buttons'],
                parse_mode=ParseMode.MARKDOWN,
                reply=False
            )
        else:
            await message.reply(
                'Something went wrong when creating a transaction',
                parse_mode=ParseMode.MARKDOWN,
                reply=False
            )


@dp.callback_query_handler(keyboards.custom_callback.filter(action=['cancel']), state=TenantStates.CAN_ADD_METERS)
async def push_cancel_button(call: types.CallbackQuery):
    await call.message.reply("Okay", reply_markup=keyboards.put_meters_kb)


@dp.callback_query_handler(keyboards.custom_callback.filter(action=["back_to_modules"]), state=TenantStates.CAN_ADD_METERS)
async def push_cancel_button(call: types.CallbackQuery):
    module_buttons = keyboards.create_buttons(
        list(GLOBAL_USER_VARS[str(call.from_user.id)]['dict_modules'].keys()),
        num_rows=3,
        prefix='Module '
    )
    await call.message.reply("Okay", reply_markup=module_buttons, reply=False)


@dp.message_handler(content_types=ContentType.PHOTO, state='*')
@dp.message_handler(content_types=ContentType.CONTACT, state='*')
@dp.message_handler(content_types=ContentType.AUDIO, state='*')
@dp.message_handler(content_types=ContentType.DOCUMENT, state='*')
@dp.message_handler(content_types=ContentType.LOCATION, state='*')
@dp.message_handler(content_types=ContentType.STICKER, state='*')
@dp.message_handler(content_types=ContentType.VOICE, state='*')
async def unknown_message(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    logging.info('Current state is %r', current_state)
    message_text = text(emojize("I don't know what to do with it :astonished:\n"
                                "I'll just remind you that there is an /info command"))
    if current_state == TenantStates.SEND_AUTH_NUMBER.state:
        await message.reply(
            message_text,
            reply_markup=keyboards.tenant_invitation_kb,
            parse_mode=ParseMode.MARKDOWN,
            reply=False
        )
    elif current_state == TenantStates.ADD_USER_INFO.state:
        await message.reply(
            message_text,
            reply_markup=keyboards.tenant_info_kb,
            parse_mode=ParseMode.MARKDOWN,
            reply=False
        )
    elif current_state == TenantStates.CAN_ADD_METERS.state:
        await message.reply(
            message_text,
            reply_markup=keyboards.put_meters_kb,
            parse_mode=ParseMode.MARKDOWN,
            reply=False
        )


if __name__ == '__main__':
    TOKEN = br.authorize_bot(BOT_AUTH_PARAMS)
    executor.start_polling(dp, on_shutdown=shutdown)
