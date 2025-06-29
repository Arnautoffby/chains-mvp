"""
/**
 * @file: env.py
 * @description: Alembic окружение для миграций
 * @dependencies: SQLAlchemy, Alembic
 * @created: 2025-06-28
 */
"""

from __future__ import annotations

import asyncio
import logging
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from bot.config import get_settings
from db.base import Base
from db import models  # noqa: F401: импорт важен для регистрации моделей

# Этот раздел опционально читает конфигурацию логирования Alembic.
config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

logger = logging.getLogger("alembic.env")
settings = get_settings()

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Запуск миграций в offline-режиме."""

    url = str(settings.db.url)
    context.configure(url=url, target_metadata=target_metadata, literal_binds=True, dialect_opts={"paramstyle": "named"})

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Запуск миграций в online-режиме."""

    connectable: AsyncEngine = create_async_engine(str(settings.db.url), poolclass=pool.NullPool)

    async def run_async_migrations() -> None:
        async with connectable.connect() as connection:  # type: ignore[arg-type]
            await connection.run_sync(do_run_migrations)

    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online() 