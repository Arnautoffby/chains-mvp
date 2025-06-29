"""
/**
 * @file: session.py
 * @description: Асинхронный движок и фабрика сессий SQLAlchemy
 * @dependencies: SQLAlchemy
 * @created: 2025-06-28
 */
"""

from __future__ import annotations

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from bot.config import get_settings

settings = get_settings()

# SQLAlchemy async engine
engine = create_async_engine(str(settings.db.url), echo=False, pool_pre_ping=True)

# Фабрика сессий
async_session_factory = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """Провайдер асинхронной сессии для использования в DI."""

    async with async_session_factory() as session:
        yield session
