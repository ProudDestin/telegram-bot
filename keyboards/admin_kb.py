from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

button_load_menu = KeyboardButton('/Загрузить меню')
button_edit_info = KeyboardButton('/Изменить информацию о кафе')
button_delete = KeyboardButton('/Удалить')
button_booking = KeyboardButton('/Посмотреть бронирования')

button_case_admin = ReplyKeyboardMarkup(resize_keyboard=True).add(button_load_menu, button_delete)\
    .add(button_edit_info).add(button_booking)
