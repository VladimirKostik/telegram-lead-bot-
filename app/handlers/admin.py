from aiogram import Bot, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from ..database.database import get_session
from ..database.repositories import (
    get_application_by_public_number,
    get_application_owner_telegram_id,
    get_applications_by_status,
    update_application_status_by_public_number,
)
from ..keyboards.admin import (
    admin_application_keyboard,
    admin_menu_keyboard,
)
from ..keyboards.main import main_keyboard
from ..security import can_modify_application, is_admin
from ..services.notifications import notify_user_status_changed


router = Router()


STATUS_LABELS = {
    "NEW": "🆕 Нова",
    "IN_PROGRESS": "🟡 В роботі",
    "DONE": "🟢 Виконано",
    "CANCELLED": "🔴 Скасовано",
}


STATUS_TITLES = {
    "NEW": "📥 Нові заявки",
    "IN_PROGRESS": "🟡 Заявки в роботі",
    "DONE": "🟢 Виконані заявки",
    "CANCELLED": "🔴 Скасовані заявки",
}


def application_text(application) -> str:
    return (
        f"📨 <b>Заявка</b>\n\n"
        f"🆔 #{application.public_number}\n"
        f"👤 Ім'я: {application.name}\n"
        f"📞 Телефон: {application.phone}\n"
        f"🔧 Послуга: {application.service}\n"
        f"💬 Коментар: {application.comment or '-'}\n"
        f"📌 Статус: "
        f"{STATUS_LABELS.get(application.status, application.status)}\n"
        f"🕐 {application.created_at.strftime('%d.%m.%Y %H:%M')}"
    )


async def show_applications_by_status(
    message: Message,
    state: FSMContext,
    status: str,
) -> None:
    if not is_admin(message.from_user.id):
        await message.answer(
            "⛔ У вас немає доступу до адміністративної панелі.",
            reply_markup=main_keyboard(is_admin=False),
        )
        return

    await state.clear()

    async with get_session() as session:
        applications = await get_applications_by_status(
            session=session,
            status=status,
        )

    title = STATUS_TITLES.get(
        status,
        "📋 Заявки",
    )

    if not applications:
        await message.answer(
            f"{title}\n\n"
            "Заявок у цьому статусі немає.",
            reply_markup=admin_menu_keyboard(),
        )
        return

    await message.answer(
        f"{title}: {len(applications)}",
        reply_markup=admin_menu_keyboard(),
    )

    for application in applications:
        await message.answer(
            application_text(application),
            reply_markup=admin_application_keyboard(
                public_number=application.public_number,
                status=application.status,
            ),
            parse_mode="HTML",
        )


@router.message(
    lambda message: message.text == "📥 Нові заявки"
)
async def show_new_applications(
    message: Message,
    state: FSMContext,
):
    await show_applications_by_status(
        message=message,
        state=state,
        status="NEW",
    )


@router.message(
    lambda message: message.text == "🟡 В роботі"
)
async def show_in_progress_applications(
    message: Message,
    state: FSMContext,
):
    await show_applications_by_status(
        message=message,
        state=state,
        status="IN_PROGRESS",
    )


@router.message(
    lambda message: message.text == "🟢 Виконані"
)
async def show_done_applications(
    message: Message,
    state: FSMContext,
):
    await show_applications_by_status(
        message=message,
        state=state,
        status="DONE",
    )


@router.message(
    lambda message: message.text == "🔴 Скасовані"
)
async def show_cancelled_applications(
    message: Message,
    state: FSMContext,
):
    await show_applications_by_status(
        message=message,
        state=state,
        status="CANCELLED",
    )


@router.message(
    lambda message: message.text == "🏠 Головне меню"
)
async def return_to_main_menu(
    message: Message,
    state: FSMContext,
):
    await state.clear()

    await message.answer(
        "Повертаю вас до головного меню:",
        reply_markup=main_keyboard(
            is_admin=is_admin(message.from_user.id)
        ),
    )


@router.callback_query(
    lambda callback:
        callback.data is not None
        and callback.data.startswith("admin_")
)
async def process_admin_action(
    callback: CallbackQuery,
    bot: Bot,
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
        action, public_number_text = callback.data.rsplit(
            ":",
            1,
        )

        public_number = int(public_number_text)

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

    owner_telegram_id: int | None = None

    async with get_session() as session:
        application = None

        try:
            application = await get_application_by_public_number(
                session=session,
                public_number=public_number,
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

            owner_telegram_id = (
                await get_application_owner_telegram_id(
                    session=session,
                    public_number=public_number,
                )
            )

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

    if application is None:
        await callback.answer(
            "❌ Заявку не знайдено.",
            show_alert=True,
        )
        return

    status_label = STATUS_LABELS.get(
        application.status,
        application.status,
    )

    await callback.message.edit_text(
        "✅ <b>Статус заявки змінено.</b>\n\n"
        f"🆔 #{application.public_number}\n"
        f"👤 Ім'я: {application.name}\n"
        f"📞 Телефон: {application.phone}\n"
        f"🔧 Послуга: {application.service}\n"
        f"💬 Коментар: {application.comment or '-'}\n"
        f"📌 Статус: {status_label}",
        parse_mode="HTML",
    )

    if owner_telegram_id is not None:
        await notify_user_status_changed(
            bot=bot,
            telegram_id=owner_telegram_id,
            application=application,
        )

    await callback.answer(
        f"Статус: {status_label}"
    )