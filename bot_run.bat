@echo off

call %~dp0telegram_bot\venv\Scripts\activate

cd %~dp0telegram_bot

set TOKEN=5571312875:AAFRizqOoMlNl9zJs49E1NuKCypKMKRCVj4

python bot_telegram.py

pause

