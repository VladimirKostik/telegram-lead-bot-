from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from ..config import ADMIN_IDS
from ..database.database import get_session
from ..database.repositories import (
    get_new_applications,
    update_application_status_by_public_number,
)
from ..keyboards.admin import admin_application_keyboard
from ..keyboards.main import main_keyboard
from ..security import (
    can_modify_application,
    is_admin,
)


router = Router()


STATUS_LABELS = {
    "NEW": "🆕 Нова",
    "IN_PROGRESS": "🟡 В роботі",
    "DONE": "🟢 Виконано",
    "CANCELLED": "🔴 Скасовано",
}


@router.message(
    lambda message: message.text == "📥 Нові заявки"
)
async def show_new_applications(
    message: Message,
    state: FSMContext,
):
    if not is_admin(message.from_user.id):
        await message.answer(
            "⛔ У вас немає доступу до "
            "адміністративної панелі.",
            reply_markup=main_keyboard(
                is_admin=False
            ),
        )
        return

    await state.clear()

    async with get_session() as session:
        applications = await get_new_applications(
            session=session,
        )

    if not applications:
        await message.answer(
            "📥 Нових заявок немає.",
            reply_markup=main_keyboard(
                is_admin=True
            ),
        )
        return

    await message.answer(
        f"📥 Нові заявки: {len(applications)}"
    )

    for application in applications:
        await message.answer(
            "📨 Нова заявка\n\n"
            f"🆔 #{application.public_number}\n"
            f"👤 Ім'я: {application.name}\n"
            f"📞 Телефон: {application.phone}\n"
            f"🔧 Послуга: {application.service}\n"
            f"💬 Коментар: "
            f"{application.comment or '-'}\n"
            f"📌 Статус: "
            f"{STATUS_LABELS.get(application.status, application.status)}\n"
            f"🕐 "
            f"{application.created_at.strftime('%d.%m.%Y %H:%M')}",
            reply_markup=admin_application_keyboard(
                public_number=application.public_number,
                status=application.status,
            ),
        )


@router.callback_query(
    lambda callback: (
        callback.data is not None
        and callback.data.startswith("admin_")
    )
)
async def process_admin_action(
    callback: CallbackQuery,
):
    if not is_admin(callback.from_user.id):
        await callback.answer(
            "⛔ Доступ заборонено.",
            show_alert=True,
        )
        return

    if callback.data is None:
        await callback.answer(
            "❌ Невірна команда.",
            show_alert=True,
        )
        return

    try:
        action, public_number_text = (
            callback.data.rsplit(":", 1)
        )

        public_number = int(
            public_number_text
        )

    except ValueError:
        await callback.answer(
            "❌ Невірний номер заявки.",
            show_alert=True,
        )
        return

    status_map = {
        "admin_in_progress": "IN_PROGRESS",
        "admin_done": "DONE",
        "admin_cancelled": "CANCELLED",
    }

    new_status = status_map.get(action)

    if new_status is None:
        await callback.answer(
            "❌ Невідома дія.",
            show_alert=True,
        )
        return

    async with get_session() as session:
        application = None

        try:
            from ..database.repositories import (
                get_application_by_public_number,
            )

            application = (
                await get_application_by_public_number(
                    session=session,
                    public_number=public_number,
                )
            )

            if application is None:
                await callback.answer(
                    "❌ Заявку не знайдено.",
                    show_alert=True,
                )
                return

            if not can_modify_application(
                user_id=callback.from_user.id,
                current_status=application.status,
                new_status=new_status,
            ):
                await callback.answer(
                    "⛔ Ця дія заборонена.",
                    show_alert=True,
                )
                return

            application = (
                await update_application_status_by_public_number(
                    session=session,
                    public_number=public_number,
                    status=new_status,
                )
            )

            await session.commit()

        except ValueError as error:
            await session.rollback()

            await callback.answer(
                str(error),
                show_alert=True,
            )
            return

        except Exception as error:
            await session.rollback()

            print("\n" + "=" * 60)
            print("ADMIN STATUS ERROR")
            print(f"Error type: {type(error).__name__}")
            print(f"Error message: {error}")
            print("=" * 60)

            await callback.answer(
                "❌ Не вдалося змінити статус.",
                show_alert=True,
            )
            return

    status_label = STATUS_LABELS.get(
        application.status,
        application.status,
    )

    await callback.message.edit_text(
        "✅ Статус заявки змінено.\n\n"
        f"🆔 #{application.public_number}\n"
        f"👤 Ім'я: {application.name}\n"
        f"📞 Телефон: {application.phone}\n"
        f"🔧 Послуга: {application.service}\n"
        f"💬 Коментар: "
        f"{application.comment or '-'}\n"
        f"📌 Статус: {status_label}"
    )

    await callback.answer(
        f"Статус: {status_label}"
    )