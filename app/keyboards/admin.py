from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


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
                    callback_data=(
                        f"admin_in_progress:{public_number}"
                    ),
                )
            ]
        )

        rows.append(
            [
                InlineKeyboardButton(
                    text="🔴 Скасувати",
                    callback_data=(
                        f"admin_cancelled:{public_number}"
                    ),
                )
            ]
        )

    elif status == "IN_PROGRESS":
        rows.append(
            [
                InlineKeyboardButton(
                    text="🟢 Виконано",
                    callback_data=(
                        f"admin_done:{public_number}"
                    ),
                )
            ]
        )

        rows.append(
            [
                InlineKeyboardButton(
                    text="🔴 Скасувати",
                    callback_data=(
                        f"admin_cancelled:{public_number}"
                    ),
                )
            ]
        )

    return InlineKeyboardMarkup(
        inline_keyboard=rows
    )