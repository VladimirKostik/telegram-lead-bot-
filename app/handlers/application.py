import re

from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    CallbackQuery,
    Message,
    ReplyKeyboardRemove,
)

from ..keyboards.application import confirmation_keyboard
from ..keyboards.main import main_keyboard
from ..states.application import ApplicationForm


router = Router()


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

    await callback.message.edit_text(
        "✅ Заявку підтверджено!\n\n"
        f"👤 Ім'я: {data['name']}\n"
        f"📞 Телефон: {data['phone']}\n"
        f"🔧 Послуга: {data['service']}\n"
        f"💬 Коментар: {data['comment']}\n\n"
        "Збереження в базу даних буде додано "
        "на наступному етапі."
    )

    await state.clear()

    await callback.message.answer(
        "Повертаю вас до головного меню:",
        reply_markup=main_keyboard,
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
        reply_markup=main_keyboard,
    )

    await callback.answer()


@router.callback_query(
    lambda callback: callback.data == "application_edit"
)
async def edit_application(
    callback: CallbackQuery,
    state: FSMContext,
):
    await state.set_state(ApplicationForm.name)

    await callback.message.edit_text(
        "✏️ Почнемо заповнення заявки заново.\n\n"
        "Як вас звати?"
    )

    await callback.answer()