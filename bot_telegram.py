from aiogram import executor
from create_bot import dp
from handlers import client, admin, booking
from db.db import init_firebase

from firebase_admin import db


def main():
    print('Бот онлайн!')
    init_firebase()

    # ref = db.reference('/')

    # ref.child('menu').push({
    #     "name": "Чиз-кейк ягодный",
    #     "about": "Сливочный сыр, яйца, песочное печенье, вишневый сок, сливочное масло, ягоды",
    #     "price": 200,
    #     "image": "cheezecake.jpg"
    # })

    client.register_handlers_client(dp)
    admin.register_handlers_admin(dp)
    booking.register_handlers_client(dp)
    # other.register_handlers_other(dp)

    executor.start_polling(dp, skip_updates=True)


if __name__ == "__main__":
    main()
