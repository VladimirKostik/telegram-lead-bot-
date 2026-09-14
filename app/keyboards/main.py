from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


def main_keyboard(is_admin: bool = False) -> ReplyKeyboardMarkup:
    rows = [
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
    ]

    if is_admin:
        rows.append(
            [
                KeyboardButton(text="📥 Нові заявки"),
            ]
        )

    return ReplyKeyboardMarkup(
        keyboard=rows,
        resize_keyboard=True,
    )