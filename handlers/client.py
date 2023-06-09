from utils.config import root_path
from aiogram import types, Dispatcher
from create_bot import bot, dp
from data_base import sqlite_db
import sys
import os
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from firebase_admin import db


# Get the path to the higher directory
higher_dir = os.path.abspath(os.path.join(
    os.path.dirname(__file__), '..', 'utils'))
sys.path.append(higher_dir)
higher_dir = os.path.abspath(os.path.join(
    os.path.dirname(__file__), '..', 'images'))
sys.path.append(higher_dir)

# Now you can import higher_file


async def command_start(message: types.Message):
    try:
        from keyboards.client_kb import kb_client  # Отложенный импорт
        await bot.send_message(message.from_user.id, 'Приятного аппетита', reply_markup=kb_client)
        await message.delete()
    except:
        await message.reply('Общение с ботом через ЛС, напишите ему:\nhttp://t.me/tablereserveBot')


async def working_hours_command(message: types.Message):
    await bot.send_message(message.from_user.id, 'Пн-Пт с 9:00 до 23:00, Сб-Вс с 10:00 до 01:00')


async def place_command(message: types.Message):
    await bot.send_message(message.from_user.id, 'ул. Мира 5б')


@dp.message_handler(commands=['Меню'])
async def menu_command(message: types.Message):
    # await sqlite_db.sql_read(message)

    ref = db.reference('/')

    menu = ref.child('menu').get()

    for key in menu.keys():

        product = menu[key]
        with open(os.path.join(root_path, 'menu', product['image']), 'rb') as photo:
            await bot.send_photo(message.chat.id, photo, caption=f'{product["name"]}\nОписание: {product["about"]}\nЦена: {product["price"]}₽')

    print()


async def restaurant_info_command(message: types.Message):

    # TODO: reading from db
    # await sqlite_db.sql_read_restaurant(message)
    ref = db.reference('/')
    about = ref.child('cafe-information').get()
    # about = """Добро пожаловать в уникальный ресторан, где вкус и изысканность встречаются в совершенном гармоничном танце. Наш ресторан - истинное творение искусства, которое приветствует вас своим утонченным интерьером и непревзойденной кулинарией."""

    image_path = os.path.join(root_path, 'images', 'rest.jpg')
    with open(image_path, 'rb') as photo:
        # Отправляем изображение
        await bot.send_photo(message.chat.id, photo)
        await bot.send_message(message.from_user.id, about)


async def leave_feedback(message: types.Message):
    keyboard = InlineKeyboardMarkup(row_width=5)
    stars = [InlineKeyboardButton(text='⭐️', callback_data='1'),
             InlineKeyboardButton(text='⭐️⭐️', callback_data='2'),
             InlineKeyboardButton(text='⭐️⭐️⭐️', callback_data='3'),
             InlineKeyboardButton(text='⭐️⭐️⭐️⭐️', callback_data='4'),
             InlineKeyboardButton(text='⭐️⭐️⭐️⭐️⭐️', callback_data='5')]
    keyboard.add(*stars)

    # message.message_id

    await bot.send_message(message.chat.id, 'Оцените наш сервис', reply_markup=keyboard)


# @dp.callback_query_handler(func=lambda c: True)
async def process_callback(callback_query: types.CallbackQuery):
    # Получаем оценку пользователя
    rating = int(callback_query.data)

    await bot.delete_message(chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id)
    await bot.send_message(callback_query.from_user.id, f'Вы оценили на {rating} звездочек! Спасибо!')


def register_handlers_client(dp: Dispatcher):
    dp.register_message_handler(command_start, commands=['start', 'help'])
    dp.register_message_handler(
        working_hours_command, content_types=types.ContentTypes.TEXT, regexp='^режим работы$')
    dp.register_message_handler(
        place_command, content_types=types.ContentTypes.TEXT, regexp='^расположение$')
    dp.register_message_handler(
        menu_command, content_types=types.ContentTypes.TEXT, regexp='^меню$')
    dp.register_message_handler(
        restaurant_info_command, content_types=types.ContentTypes.TEXT, regexp='^информация о ресторане$')
    dp.register_message_handler(
        leave_feedback, content_types=types.ContentTypes.TEXT, regexp='Оставить отзыв')
    dp.register_callback_query_handler(process_callback)
