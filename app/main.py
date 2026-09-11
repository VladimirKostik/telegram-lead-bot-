import asyncio
import os

from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import Message
from dotenv import load_dotenv

from .handlers.application import router as application_router
from .keyboards.main import main_keyboard


load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN is not set in .env")


dp = Dispatcher()

# Подключаем обработчик заявок
dp.include_router(application_router)


@dp.message(CommandStart())
async def start_handler(message: Message):
    await message.answer(
        "Вітаю! 👋\n\n"
        "Я допоможу залишити заявку.\n\n"
        "Оберіть потрібну дію:",
        reply_markup=main_keyboard,
    )


async def main():
    bot = Bot(token=BOT_TOKEN)

    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())