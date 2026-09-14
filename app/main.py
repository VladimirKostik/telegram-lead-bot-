import asyncio

from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import Message

from .config import ADMIN_IDS, BOT_TOKEN
from .database.database import init_db
from .handlers import admin, application
from .keyboards.main import main_keyboard


def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS


dp = Dispatcher()


@dp.message(CommandStart())
async def start_handler(message: Message):
    await message.answer(
        "Вітаю! 👋\n\n"
        "Я допоможу вам залишити заявку.\n\n"
        "Оберіть потрібну дію:",
        reply_markup=main_keyboard(
            is_admin=is_admin(message.from_user.id)
        ),
    )


async def main():
    await init_db()

    bot = Bot(token=BOT_TOKEN)

    dp.include_router(application.router)
    dp.include_router(admin.router)

    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())