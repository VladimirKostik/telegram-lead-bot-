from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


main_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="📝 Залишити заявку"),
        ],
        [
            KeyboardButton(text="📋 Мої заявки"),
            KeyboardButton(text="❓ FAQ"),
        ],
        [
            KeyboardButton(text="📞 Контакти"),
        ],
    ],
    resize_keyboard=True,
)