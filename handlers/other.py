from aiogram import types, Dispatcher
from create_bot import dp
import json
import string

# @dp.message_handler()
# async def echo_send(message: types.Message):
#     try:
#         censored_words = set(json.load(open('cenz.json')))
#     except FileNotFoundError:
#         censored_words = set()

#     if ({i.lower().translate(str.maketrans('', '', string.punctuation)) for i in message.text.split()}
#             .intersection(censored_words)):
#         await message.reply('Маты запрещены')
#         await message.delete()

# def register_handlers_other(dp : Dispatcher):
#     dp.register_message_handler(echo_send)