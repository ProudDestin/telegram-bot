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


class UserInfo(StatesGroup):
    waiting_for_info = State()


async def change_rest_information(message: types.Message):

    ref = db.reference('/')
    about = ref.child('cafe-information').get()

    await bot.send_message(message.from_user.id, f'Текущее описание: {about}')
    await bot.send_message(message.from_user.id, f'Введите на что поменять')
    await UserInfo.waiting_for_info.set()


@dp.message_handler(state=UserInfo.waiting_for_info)
async def process_info(message: types.Message, state: FSMContext):
    new_info = message.text

    print(new_info)


async def process_info(message: types.Message, state: FSMContext):
    new_info = message.text

    print(new_info)


def register_handlers_admin(dp: Dispatcher):
    dp.register_message_handler(change_rest_information, commands=[
                                'Изменить информацию о кафе'], state=None)

    dp.register_message_handler(
        change_rest_information, state=UserInfo.waiting_for_info)
