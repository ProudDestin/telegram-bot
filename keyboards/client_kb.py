from aiogram.types import ReplyKeyboardMarkup, KeyboardButton #, ReplyKeyboardRemove

b1 = KeyboardButton(text='Режим работы')
b2 = KeyboardButton(text='Расположение')
b3 = KeyboardButton(text='Меню')
b4 = KeyboardButton(text='Информация о ресторане')
b5 = KeyboardButton(text='Оставить отзыв')
b6 = KeyboardButton(text='Забронировать стол') 
#b4 = KeyboardButton('Поделиться номером', request_contact=True)
#b5 = KeyboardButton('Отправить где я', request_location=True )

kb_client = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
kb_client.add(b1).add(b2).add(b3).add(b4).add(b5).add(b6)



