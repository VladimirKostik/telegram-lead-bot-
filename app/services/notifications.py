from aiogram import Bot

from ..config import ADMIN_IDS
from ..database.models import Application


STATUS_LABELS = {
    "NEW": "🆕 Нова",
    "IN_PROGRESS": "🟡 В роботі",
    "DONE": "🟢 Виконано",
    "CANCELLED": "🔴 Скасовано",
}


async def notify_admins(
    bot: Bot,
    application: Application,
) -> None:
    message_text = (
        "🔔 <b>Нова заявка</b>\n\n"
        f"🆔 #{application.public_number}\n"
        f"👤 Ім'я: {application.name}\n"
        f"📞 Телефон: {application.phone}\n"
        f"🔧 Послуга: {application.service}\n"
        f"💬 Коментар: {application.comment or '-'}\n"
        f"📌 Статус: "
        f"{STATUS_LABELS.get(application.status, application.status)}\n\n"
        "Відкрийте адміністративне меню, "
        "щоб обробити заявку."
    )

    for admin_id in ADMIN_IDS:
        try:
            await bot.send_message(
                chat_id=admin_id,
                text=message_text,
                parse_mode="HTML",
            )
        except Exception as error:
            print("\n" + "=" * 60)
            print("ADMIN NOTIFICATION ERROR")
            print(f"Admin ID: {admin_id}")
            print(f"Error type: {type(error).__name__}")
            print(f"Error message: {error}")
            print("=" * 60)


async def notify_user_status_changed(
    bot: Bot,
    telegram_id: int,
    application: Application,
) -> None:
    status_label = STATUS_LABELS.get(
        application.status,
        application.status,
    )

    if application.status == "DONE":
        text = (
            f"✅ <b>Заявку #{application.public_number} "
            "виконано.</b>\n\n"
            f"📌 Статус: {status_label}"
        )

    elif application.status == "CANCELLED":
        text = (
            f"🔴 <b>Заявку #{application.public_number} "
            "скасовано.</b>\n\n"
            f"📌 Статус: {status_label}"
        )

    elif application.status == "IN_PROGRESS":
        text = (
            f"🔔 <b>Статус заявки "
            f"#{application.public_number} змінено.</b>\n\n"
            f"📌 Статус: {status_label}"
        )

    else:
        text = (
            f"🔔 <b>Статус заявки "
            f"#{application.public_number} змінено.</b>\n\n"
            f"📌 Статус: {status_label}"
        )

    try:
        await bot.send_message(
            chat_id=telegram_id,
            text=text,
            parse_mode="HTML",
        )
    except Exception as error:
        print("\n" + "=" * 60)
        print("USER NOTIFICATION ERROR")
        print(f"Telegram ID: {telegram_id}")
        print(f"Error type: {type(error).__name__}")
        print(f"Error message: {error}")
        print("=" * 60)