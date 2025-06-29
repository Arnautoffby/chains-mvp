"""
/**
 * @file: config.py
 * @description: Загрузка конфигурации из переменных окружения / файла .env
 * @dependencies: python-dotenv, pydantic
 * @created: 2025-06-28
 */
"""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv
from pydantic import BaseModel, Field, PostgresDsn

# Загружаем .env, если существует
load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent / ".env", override=True)


class BotSettings(BaseModel):
    token: str = Field(..., env="BOT_TOKEN")


class DatabaseSettings(BaseModel):
    url: PostgresDsn = Field(..., env="DATABASE_URL")


class GameSettings(BaseModel):
    payment_addresses: list[str] = Field(
        default=[
            "TQ1xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
            "TQ2xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
            "TQ3xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
            "TQ4xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
            "TQ5xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
            "TQ6xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
            "TQ7xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
            "TQ8xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
            "TQ9xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
            "TQ10xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
        ]
    )


class TronScanSettings(BaseModel):
    api_url: str = Field("https://apilist.tronscanapi.com/api", env="TRONSCAN_API_URL")
    api_key: str | None = Field(None, env="TRONSCAN_API_KEY")


class Settings(BaseModel):
    bot: BotSettings = BotSettings()
    db: DatabaseSettings = DatabaseSettings()
    game: GameSettings = GameSettings()
    tron: TronScanSettings = TronScanSettings()


@lru_cache()
def get_settings() -> Settings:
    """Возвращает singleton настроек, загруженных из окружения."""

    return Settings() 