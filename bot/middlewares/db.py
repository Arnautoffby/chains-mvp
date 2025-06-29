"""
/**
 * @file: db.py
 * @description: Middleware для предоставления SQLAlchemy AsyncSession в хэндлерах aiogram
 * @dependencies: aiogram, db.session
 * @created: 2025-06-28
 */
"""

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from typing import Any, Callable, Dict, Awaitable

from db.session import async_session_factory


class DBSessionMiddleware(BaseMiddleware):
    """Создаёт новую сессию на время обработки апдейта."""

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        async with async_session_factory() as session:
            data["session"] = session
            return await handler(event, data)
