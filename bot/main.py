"""
/**
 * @file: main.py
 * @description: Точка входа Telegram-бота Chains – базовые команды /start и /help
 * @dependencies: aiogram, config.py
 * @created: 2025-06-28
 */
"""

import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.storage.memory import MemoryStorage

from bot.config import get_settings
from db.session import async_session_factory
from bot.services.chains import expire_old_slots

logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(name)s | %(message)s")
logger = logging.getLogger(__name__)

settings = get_settings()

bot = Bot(token=settings.bot.token, parse_mode=ParseMode.HTML)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# Подключаем middleware
from bot.middlewares.db import DBSessionMiddleware

dp.message.middleware(DBSessionMiddleware())

# Роутеры
from bot.handlers import registration as registration_router  # noqa: E402
from bot.handlers import status as status_router  # noqa: E402
from bot.handlers import team as team_router  # noqa: E402

dp.include_router(registration_router.router)
dp.include_router(status_router.router)
dp.include_router(team_router.router)


@dp.message(Command("help"))
async def cmd_help(message: Message) -> None:
    """Обработка /help."""

    await message.answer(
        "Список команд:\n"
        "/start – начать работу с ботом\n"
        "/help – справка"
    )


async def _cron_expire_slots() -> None:
    while True:
        async with async_session_factory() as sess:
            await expire_old_slots(sess)
            await sess.commit()
        await asyncio.sleep(600)  # 10 минут


def main() -> None:
    """Запуск бота."""

    logger.info("Starting bot")
    try:
        async def runner():
            task = asyncio.create_task(_cron_expire_slots())
            try:
                await dp.start_polling(bot)
            finally:
                task.cancel()
        asyncio.run(runner())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot stopped")


if __name__ == "__main__":
    main() 