"""
/**
 * @file: registration.py
 * @description: Хэндлеры регистрации пользователя, запрос USDT-кошелька и проверка оплаты
 * @dependencies: aiogram, db.models, bot.services.payments
 * @created: 2025-06-28
 */
"""

from __future__ import annotations

import re
from typing import Optional

from aiogram import Router, Bot
from aiogram.filters import CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import User, UserStatus
from bot.config import get_settings
from bot.services.payments import create_pending_payments, verify_payments

router = Router()


class RegistrationStates(StatesGroup):
    waiting_wallet = State()
    waiting_payment = State()


WALLET_RE = re.compile(r"^[a-zA-Z0-9]{20,70}$")


def _build_invite_link(bot_username: str, user_id: int) -> str:
    return f"https://t.me/{bot_username}?start={user_id}"


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext, session: AsyncSession, bot: Bot) -> None:
    """Старт: создаём или находим пользователя и переводим в процесс регистрации."""

    telegram_id = str(message.from_user.id)

    result = await session.execute(select(User).where(User.telegram_id == telegram_id))
    user: Optional[User] = result.scalar_one_or_none()

    if user is None:
        user = User(telegram_id=telegram_id, usdt_wallet="", status=UserStatus.pending)
        session.add(user)
        await session.commit()

    if not user.usdt_wallet:
        await message.answer("Пожалуйста, отправьте адрес вашего <b>USDT (TRC-20)</b> кошелька.")
        await state.set_state(RegistrationStates.waiting_wallet)
        return

    if user.status == UserStatus.pending:
        await send_payment_instructions(message, user, state)
        return

    # Пользователь активен – отдаём инвайт
    invite_link = _build_invite_link((await bot.get_me()).username, user.id)
    await message.answer(
        "Вы уже активированы!\n"
        f"Ваша инвайт-ссылка: {invite_link}"
    )


@router.message(StateFilter(RegistrationStates.waiting_wallet))
async def wallet_received(message: Message, state: FSMContext, session: AsyncSession, bot: Bot) -> None:
    """Обрабатываем отправленный кошелёк пользователя."""

    wallet = message.text.strip()
    if not WALLET_RE.fullmatch(wallet):
        await message.answer("Неверный формат кошелька. Попробуйте снова.")
        return

    telegram_id = str(message.from_user.id)
    result = await session.execute(select(User).where(User.telegram_id == telegram_id))
    user: User = result.scalar_one()

    user.usdt_wallet = wallet
    user.status = UserStatus.pending
    await session.commit()

    # Создаём записи ожидаемых платежей (chain_id=0 – MVP)
    await create_pending_payments(session, chain_id=0, from_wallet=wallet)

    await send_payment_instructions(message, user, state)


async def send_payment_instructions(message: Message, user: User, state: FSMContext) -> None:
    """Шлём список адресов для перевода и кнопку `Готово✅`."""

    settings = get_settings()

    addresses_list = "\n".join(
        [f"{idx + 1}. <code>{addr}</code>" for idx, addr in enumerate(settings.game.payment_addresses)]
    )

    ready_kb = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="Готово✅")]], resize_keyboard=True, one_time_keyboard=True
    )

    await message.answer(
        "Переведите <b>по $1 USDT</b> на каждый из следующих адресов (TRC-20):\n\n"
        f"{addresses_list}\n\n"
        "После отправки всех 10 платежей нажмите кнопку <b>Готово✅</b>.",
        reply_markup=ready_kb,
    )

    await state.set_state(RegistrationStates.waiting_payment)


@router.message(StateFilter(RegistrationStates.waiting_payment))
async def payment_done(message: Message, state: FSMContext, session: AsyncSession, bot: Bot) -> None:
    """Проверяем платежи после нажатия 'Готово✅'."""

    if message.text.strip().lower() not in {"готово✅", "готово", "gotovo"}:
        await message.answer("Пожалуйста, нажмите кнопку <b>Готово✅</b> после всех переводов.")
        return

    telegram_id = str(message.from_user.id)
    result = await session.execute(select(User).where(User.telegram_id == telegram_id))
    user: User = result.scalar_one()

    verified = await verify_payments(session, user_wallet=user.usdt_wallet, chain_id=0)

    if not verified:
        await message.answer("Оплата не найдена. Проверьте транзакции и попробуйте позже.")
        return

    user.status = UserStatus.active
    await session.commit()

    invite_link = _build_invite_link((await bot.get_me()).username, user.id)

    await message.answer(
        "Оплата подтверждена! 🎉\n\n"
        f"Ваша инвайт-ссылка: {invite_link}\n\n"
        "Пригласите X друзей, чтобы продвигаться дальше.",
        reply_markup=None,
    )

    await state.clear()