from aiogram.dispatcher import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram import types
from create_bot import dp, bot
from aiogram.dispatcher.filters import Text
from data_base import sqlite_db
from keyboards import admin_kb
import os
import sys
from firebase_admin import db

from utils.config import root_path

ID = None

higher_dir = os.path.abspath(os.path.join(
    os.path.dirname(__file__), '..', 'utils'))
sys.path.append(higher_dir)
higher_dir = os.path.abspath(os.path.join(
    os.path.dirname(__file__), '..', 'images'))
sys.path.append(higher_dir)


class FSMAdmin(StatesGroup):
    photo = State()
    name = State()
    description = State()
    price = State()
    restaurant_info = State()

# Получение id текущего модератора
# @dp.message_handler(commands=['moderator'], is_chat_admin=True)


async def make_changes_command(message: types.Message):
    global ID
    ID = message.from_user.id
    await bot.send_message(message.from_user.id, 'Здравствуйте, администратор', reply_markup=admin_kb.button_case_admin)
    # await message.delete()

# Начало диалога загрузки нового пункта меню
# @dp.message_handler(commands='Загрузить', state=None)


async def cm_start(message: types.Message):
    if message.from_user.id == ID:
        await FSMAdmin.photo.set()
        await message.reply('Загрузи фото')

# Выход из состояний
# @dp.message_handler(state="*", commands='отмена')
# @dp.message_handler(Text(equals='отмена', ignore_case=True), state="*")


async def cancel_handler(message: types.Message, state: FSMContext):
    if message.from_user.id == ID:
        current_state = await state.get_state()
        if current_state is None:
            return
        await state.finish()
        await message.reply('OK')

# Получение ответа и запись в словарь
# @dp.message_handler(content_types=['photo'], state=FSMAdmin.photo)


# async def load_photo(message: types.Message, state: FSMContext):
#     if message.from_user.id == ID:
#         async with state.proxy() as data:
#             data['photo'] = message.photo[0].file_id
#         await FSMAdmin.next()
#         await message.reply("Введи название")


async def load_photo(message: types.Message, state: FSMContext):
    if message.from_user.id == ID:
        async with state.proxy() as data:
            data['photo'] = message.photo[-1].file_id

        # Save the photo to a directory
        photo_path = os.path.join(root_path, 'menu', f"{data['photo']}.jpg")
        photo_file = await bot.get_file(data['photo'])
        await photo_file.download(destination_file=photo_path)

        await FSMAdmin.next()
        await message.reply("Введи название")

# Получение второго ответа
# @dp.message_handler(state=FSMAdmin.name)


async def load_name(message: types.Message, state: FSMContext):
    if message.from_user.id == ID:
        async with state.proxy() as data:
            data['name'] = message.text
        await FSMAdmin.next()
        await message.reply("Введи описание")

# Получение третьего ответа
# @dp.message_handler(state=FSMAdmin.description)


async def load_description(message: types.Message, state: FSMContext):
    if message.from_user.id == ID:
        async with state.proxy() as data:
            data['description'] = message.text
        await FSMAdmin.next()
        await message.reply("Укажи цену")

# Получение последнего ответа и использование полученных данных
# @dp.message_handler(state=FSMAdmin.price)


# async def load_price(message: types.Message, state: FSMContext):
#     if message.from_user.id == ID:
#         async with state.proxy() as data:
#             data['price'] = float(message.text)
#         # await sqlite_db.sql_add_command(state)

#         # ref = db.reference('/')

#         print(state["photo"])
#         print(state["description"])

#         # booking = ref.child('booking')

#         await state.finish()


async def load_price(message: types.Message, state: FSMContext):
    if message.from_user.id == ID:
        async with state.proxy() as data:
            data['price'] = float(message.text)

        # Process the collected data

        # Retrieve the photo file ID from the stored data
        photo_file_id = data.get('photo')

        name = data.get("name")
        about = data.get("description")
        price = data.get("price")

        ref = db.reference('/')
        menu = ref.child('menu')

        menu.push({
            "name": name,
            "about": about,
            "price": price,
            "image": f"{photo_file_id}.jpg"
        })

        await state.finish()
        await message.reply("Добавлено")


class UserInfo(StatesGroup):
    waiting_for_info = State()


async def change_rest_information(message: types.Message):

    ref = db.reference('/')
    about = ref.child('cafe-information').get()

    await bot.send_message(message.from_user.id, f'Текущее описание: {about}')
    await bot.send_message(message.from_user.id, 'Введите на что поменять')
    await UserInfo.waiting_for_info.set()


async def process_info(message: types.Message, state: FSMContext):
    new_info = message.text

    ref = db.reference('/')
    ref.child('cafe-information').set(new_info)

    await bot.send_message(message.from_user.id, f'Изменено на: {new_info}')
    await state.finish()


class DeleteMenuState(StatesGroup):
    waiting_for_number = State()


async def delete_from_menu(message: types.Message):

    ref = db.reference('/')
    menu = ref.child('menu').get()

    names = []

    i = 1

    for key in menu.keys():
        s = menu[key]["name"]
        names.append(f"{i}. {s}")

        i += 1

    await bot.send_message(message.from_user.id, '\n'.join(names))
    await bot.send_message(message.from_user.id, 'Введите номер который хотите удалить')
    await DeleteMenuState.waiting_for_number.set()


async def process_number(message: types.Message, state: FSMContext):
    number = message.text

    ref = db.reference('/')
    menu = ref.child('menu').get()

    key = list(menu.keys())[int(number)-1]
    ref.child('menu').child(key).delete()
    await bot.send_message(message.from_user.id, 'Удалено')
    await state.finish()


async def check_booking(message: types.Message):

    ref = db.reference('/')
    booking = ref.child('booking').get()

    for key in booking.keys():

        b = booking[key]

        await bot.send_message(message.from_user.id, f'Имя: {b["name"]}\nКол-во: {b["people"]}\nТелефон: {b["phone"]}\nДата: ${b["date"]}\nВремя: {b["time"]}')


async def check_rating(message: types.Message):
    ref = db.reference('/')
    rating = ref.child('rating').get()

    for key in rating.keys():
        r = rating[key]
        await bot.send_message(message.from_user.id, f'Оценка: {r}')


def register_handlers_admin(dp: Dispatcher):
    dp.register_message_handler(cm_start, commands=['Загрузить'], state=None)
    dp.register_message_handler(cancel_handler, state="*", commands='отмена')
    dp.register_message_handler(cancel_handler, Text(
        equals='отмена', ignore_case=True), state="*")
    dp.register_message_handler(load_photo, content_types=[
                                'photo'], state=FSMAdmin.photo)
    dp.register_message_handler(load_name, state=FSMAdmin.name)
    dp.register_message_handler(load_description, state=FSMAdmin.description)
    dp.register_message_handler(load_price, state=FSMAdmin.price)
    dp.register_message_handler(make_changes_command, commands=[
                                'moderator'], is_chat_admin=True)

    dp.register_message_handler(change_rest_information, commands=['Изменить'])
    dp.register_message_handler(process_info, state=UserInfo.waiting_for_info)

    dp.register_message_handler(delete_from_menu, commands=['Удалить'])
    dp.register_message_handler(
        process_number, state=DeleteMenuState.waiting_for_number)

    dp.register_message_handler(check_booking, commands=['Посмотреть'])
    dp.register_message_handler(check_rating, commands=['Оценки'])
