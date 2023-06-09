import firebase_admin
from firebase_admin import credentials
from utils.config import root_path
import os


def init_firebase():
    cred = credentials.Certificate(
        os.path.join(root_path, 'db', 'telegram-bot-219eb-firebase-adminsdk-v0p9z-eff37e0195.json'))
    firebase_admin.initialize_app(cred, {
        "databaseURL": "https://telegram-bot-219eb-default-rtdb.firebaseio.com"
    })
