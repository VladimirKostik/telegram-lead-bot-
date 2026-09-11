from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


confirmation_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="✅ Підтвердити",
                callback_data="application_confirm",
            )
        ],
        [
            InlineKeyboardButton(
                text="✏️ Змінити",
                callback_data="application_edit",
            ),
            InlineKeyboardButton(
                text="❌ Скасувати",
                callback_data="application_cancel",
            ),
        ],
    ]
)