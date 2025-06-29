"""
/**
 * @file: base.py
 * @description: Базовый declarative класс SQLAlchemy
 * @dependencies: SQLAlchemy
 * @created: 2025-06-28
 */
"""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Базовый класс для всех моделей."""

    pass 