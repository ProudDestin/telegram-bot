from create_bot import bot, dp
from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from keyboards.client_kb import kb_client
from firebase_admin import db

time_options = ['10:00', '12:00', '15:00', '18:00']


class BookingForm(StatesGroup):
    name = State()
    phone = State()
    people = State()
    date = State()
    time = State()
    confirmation = State()


def get_back_keyboard():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(types.KeyboardButton('Назад'))
    return keyboard


async def start_booking(message: types.Message):
    await message.answer('Введите ваше имя:', reply_markup=kb_client)
    await BookingForm.name.set()


@dp.message_handler(state=BookingForm.name)
async def process_name(message: types.Message, state: FSMContext):

    async with state.proxy() as data:
        data['name'] = message.text

    await message.answer('Введите ваш номер телефона:', reply_markup=get_back_keyboard())
    await BookingForm.phone.set()


@dp.message_handler(state=BookingForm.phone)
async def process_phone(message: types.Message, state: FSMContext):
    if message.text.lower() == 'назад':
        # Go back to the previous step
        await BookingForm.name.set()
        async with state.proxy() as data:
            data.pop('name', None)
        await message.answer('Введите ваше имя:', reply_markup=get_back_keyboard())
        return

    if not message.text:
        await message.answer('Некорректный ввод. Введите ваш номер телефона или "Назад".',
                             reply_markup=get_back_keyboard())
        return

    async with state.proxy() as data:
        data['phone'] = message.text

    await message.answer('Введите количество человек:', reply_markup=get_back_keyboard())
    await BookingForm.people.set()


@dp.message_handler(state=BookingForm.people)
async def process_people(message: types.Message, state: FSMContext):
    if message.text.lower() == 'назад':
        # Go back to the previous step
        await BookingForm.phone.set()
        async with state.proxy() as data:
            data.pop('phone', None)
        await message.answer('Введите ваш номер телефона:', reply_markup=get_back_keyboard())
        return

    if not message.text or not message.text.isdigit():
        await message.answer('Некорректный ввод. Введите количество человек или "Назад".',
                             reply_markup=get_back_keyboard())
        return

    async with state.proxy() as data:
        data['people'] = message.text

    await message.answer('Введите дату бронирования (в формате ДД.ММ.ГГГГ):', reply_markup=get_back_keyboard())
    await BookingForm.date.set()


@dp.message_handler(state=BookingForm.date)
async def process_date_message(message: types.Message, state: FSMContext):
    if message.text.lower() == 'назад':
        # Go back to the previous step
        await BookingForm.people.set()
        async with state.proxy() as data:
            data.pop('people', None)
        await message.reply('Введите количество человек:', reply_markup=get_back_keyboard())
        return

    async with state.proxy() as data:
        data['date'] = message.text

    await message.reply('Введите время бронирования:', reply_markup=get_time_keyboard())

    await BookingForm.time.set()


@dp.callback_query_handler(lambda c: c.data.startswith('time_'), state=BookingForm.time)
async def process_time_callback(callback_query: types.CallbackQuery, state: FSMContext):
    time_option = callback_query.data.split('_')[1]
    async with state.proxy() as data:
        data['time'] = time_option

    async with state.proxy() as data:
        confirmation_message = f'Бронирование успешно!\n\n' \
                               f'Имя: {data["name"]}\n' \
                               f'Телефон: {data["phone"]}\n' \
                               f'Количество человек: {data["people"]}\n' \
                               f'Дата: {data["date"]}\n' \
                               f'Время: {data["time"]}'

    # Perform further actions with the collected information
    # For this example, we simply send a confirmation message
    confirm_button = InlineKeyboardButton(
        'Подтвердить', callback_data='confirm')
    cancel_button = InlineKeyboardButton('Отменить', callback_data='cancel')
    confirmation_keyboard = InlineKeyboardMarkup().add(confirm_button, cancel_button)

    await callback_query.message.reply(confirmation_message, reply_markup=confirmation_keyboard)

    # Set the state to the confirmation step
    await BookingForm.confirmation.set()


@dp.callback_query_handler(lambda c: c.data == 'confirm', state=BookingForm.confirmation)
async def confirm_booking(callback_query, state: FSMContext):
    async with state.proxy() as data:
        # Access the collected information
        name = data['name']
        phone = data['phone']
        people = data['people']
        date = data['date']
        time = data['time']

        # Perform the booking or any other required action
        # ...

    await callback_query.message.reply('Бронирование подтверждено!', reply_markup=kb_client)

    ref = db.reference('/')

    booking = ref.child('booking')

    booking.push({
        "name": name,
        "phone": phone,
        "people": people,
        "date": date,
        "time": time
    })

    # Reset the state to start a new booking
    await state.finish()


@dp.callback_query_handler(lambda c: c.data == 'cancel', state=BookingForm.confirmation)
async def cancel_booking(callback_query, state: FSMContext):
    await callback_query.message.reply('Бронирование отменено!', reply_markup=kb_client)

    # Reset the state to start a new booking
    await state.finish()


def get_time_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=2)

    for time_option in time_options:
        keyboard.add(InlineKeyboardButton(
            time_option, callback_data=f'time_{time_option}'))

    return keyboard


def register_handlers_client(dp: Dispatcher):
    dp.register_message_handler(
        start_booking, content_types=types.ContentTypes.TEXT, regexp='^забронировать стол$')
