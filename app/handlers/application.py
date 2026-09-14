import re

from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    CallbackQuery,
    Message,
    ReplyKeyboardRemove,
)

from ..config import ADMIN_IDS
from ..database.database import get_session
from ..database.repositories import (
    create_application,
    get_or_create_user,
    get_user_applications,
)
from ..keyboards.application import confirmation_keyboard
from ..keyboards.main import main_keyboard
from ..states.application import ApplicationForm


router = Router()


def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS


@router.message(
    lambda message: message.text == "📝 Залишити заявку"
)
async def start_application(
    message: Message,
    state: FSMContext,
):
    await state.set_state(ApplicationForm.name)

    await message.answer(
        "Як вас звати?",
        reply_markup=ReplyKeyboardRemove(),
    )


@router.message(ApplicationForm.name)
async def process_name(
    message: Message,
    state: FSMContext,
):
    name = (message.text or "").strip()

    if len(name) < 2:
        await message.answer(
            "Будь ласка, введіть ваше ім'я "
            "(мінімум 2 символи)."
        )
        return

    await state.update_data(name=name)
    await state.set_state(ApplicationForm.phone)

    await message.answer(
        "Вкажіть ваш номер телефону:\n\n"
        "Наприклад: +380501234567"
    )


@router.message(ApplicationForm.phone)
async def process_phone(
    message: Message,
    state: FSMContext,
):
    phone = (message.text or "").strip()

    phone_pattern = r"^\+?[0-9\s\-\(\)]{10,20}$"

    if not re.fullmatch(phone_pattern, phone):
        await message.answer(
            "Невірний формат номера телефону.\n\n"
            "Приклад: +380501234567"
        )
        return

    await state.update_data(phone=phone)
    await state.set_state(ApplicationForm.service)

    await message.answer(
        "Яка послуга вас цікавить?"
    )


@router.message(ApplicationForm.service)
async def process_service(
    message: Message,
    state: FSMContext,
):
    service = (message.text or "").strip()

    if len(service) < 2:
        await message.answer(
            "Будь ласка, вкажіть послугу."
        )
        return

    await state.update_data(service=service)
    await state.set_state(ApplicationForm.comment)

    await message.answer(
        "Додайте коментар до заявки "
        "або напишіть «-», якщо коментар не потрібен:"
    )


@router.message(ApplicationForm.comment)
async def process_comment(
    message: Message,
    state: FSMContext,
):
    comment = (message.text or "").strip()

    await state.update_data(comment=comment)

    data = await state.get_data()

    await message.answer(
        "Перевірте вашу заявку:\n\n"
        f"👤 Ім'я: {data['name']}\n"
        f"📞 Телефон: {data['phone']}\n"
        f"🔧 Послуга: {data['service']}\n"
        f"💬 Коментар: {data['comment']}\n\n"
        "Все правильно?"
    )

    await message.answer(
        "Оберіть дію:",
        reply_markup=confirmation_keyboard,
    )


@router.callback_query(
    lambda callback: callback.data == "application_confirm"
)
async def confirm_application(
    callback: CallbackQuery,
    state: FSMContext,
):
    data = await state.get_data()

    try:
        async with get_session() as session:
            user = await get_or_create_user(
                session=session,
                telegram_id=callback.from_user.id,
                username=callback.from_user.username,
                first_name=callback.from_user.first_name,
            )

            application = await create_application(
                session=session,
                user=user,
                name=data["name"],
                phone=data["phone"],
                service=data["service"],
                comment=data["comment"],
            )

            await session.commit()

        await callback.message.edit_text(
            "✅ Заявку підтверджено!\n\n"
            f"🆔 Номер заявки: #{application.public_number}\n"
            f"👤 Ім'я: {application.name}\n"
            f"📞 Телефон: {application.phone}\n"
            f"🔧 Послуга: {application.service}\n"
            f"💬 Коментар: {application.comment}\n\n"
            "Заявку успішно збережено."
        )

        await state.clear()

        await callback.message.answer(
            "Повертаю вас до головного меню:",
            reply_markup=main_keyboard(
                is_admin=is_admin(callback.from_user.id)
            ),
        )

    except Exception as error:
        print("\n" + "=" * 60)
        print("DATABASE ERROR")
        print(f"Error type: {type(error).__name__}")
        print(f"Error message: {error}")
        print("=" * 60)

        await callback.message.edit_text(
            "❌ Не вдалося зберегти заявку.\n\n"
            "Спробуйте ще раз."
        )

    await callback.answer()


@router.callback_query(
    lambda callback: callback.data == "application_cancel"
)
async def cancel_application(
    callback: CallbackQuery,
    state: FSMContext,
):
    await state.clear()

    await callback.message.edit_text(
        "❌ Створення заявки скасовано."
    )

    await callback.message.answer(
        "Повертаю вас до головного меню:",
        reply_markup=main_keyboard(
            is_admin=is_admin(callback.from_user.id)
        ),
    )

    await callback.answer()


@router.callback_query(
    lambda callback: callback.data == "application_edit"
)
async def edit_application(
    callback: CallbackQuery,
    state: FSMContext,
):
    await state.clear()
    await state.set_state(ApplicationForm.name)

    await callback.message.edit_text(
        "✏️ Почнемо заповнення заявки заново.\n\n"
        "Як вас звати?"
    )

    await callback.answer()


@router.message(
    lambda message: message.text == "📋 Мої заявки"
)
async def show_my_applications(
    message: Message,
):
    try:
        async with get_session() as session:
            applications = await get_user_applications(
                session=session,
                telegram_id=message.from_user.id,
            )

        if not applications:
            await message.answer(
                "📋 У вас поки немає заявок.",
                reply_markup=main_keyboard(
                    is_admin=is_admin(message.from_user.id)
                ),
            )
            return

        lines = ["📋 Ваші заявки:\n"]

        for application in applications:
            created_at = application.created_at.strftime(
                "%d.%m.%Y %H:%M"
            )

            lines.append(
                f"🆔 #{application.public_number}\n"
                f"🔧 Послуга: {application.service}\n"
                f"📌 Статус: {application.status}\n"
                f"💬 Коментар: {application.comment or '-'}\n"
                f"🕐 {created_at}\n"
            )

        await message.answer(
            "\n".join(lines),
            reply_markup=main_keyboard(
                is_admin=is_admin(message.from_user.id)
            ),
        )

    except Exception as error:
        print("\n" + "=" * 60)
        print("APPLICATIONS READ ERROR")
        print(f"Error type: {type(error).__name__}")
        print(f"Error message: {error}")
        print("=" * 60)

        await message.answer(
            "❌ Не вдалося отримати ваші заявки.",
            reply_markup=main_keyboard(
                is_admin=is_admin(message.from_user.id)
            ),
        )