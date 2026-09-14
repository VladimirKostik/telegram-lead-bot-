from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


def admin_application_keyboard(
    public_number: int,
    status: str,
) -> InlineKeyboardMarkup:
    rows: list[list[InlineKeyboardButton]] = []

    if status == "NEW":
        rows.append(
            [
                InlineKeyboardButton(
                    text="🟡 Взяти в роботу",
                    callback_data=f"admin_in_progress:{public_number}",
                )
            ]
        )
        rows.append(
            [
                InlineKeyboardButton(
                    text="🔴 Скасувати",
                    callback_data=f"admin_cancelled:{public_number}",
                )
            ]
        )

    elif status == "IN_PROGRESS":
        rows.append(
            [
                InlineKeyboardButton(
                    text="🟢 Виконано",
                    callback_data=f"admin_done:{public_number}",
                )
            ]
        )
        rows.append(
            [
                InlineKeyboardButton(
                    text="🔴 Скасувати",
                    callback_data=f"admin_cancelled:{public_number}",
                )
            ]
        )

    return InlineKeyboardMarkup(
        inline_keyboard=rows
    )


def admin_menu_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="📥 Нові заявки"),
                KeyboardButton(text="🟡 В роботі"),
            ],
            [
                KeyboardButton(text="🟢 Виконані"),
                KeyboardButton(text="🔴 Скасовані"),
            ],
            [
                KeyboardButton(text="🏠 Головне меню"),
            ],
        ],
        resize_keyboard=True,
    )