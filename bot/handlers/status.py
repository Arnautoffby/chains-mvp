"""
/**
 * @file: status.py
 * @description: Команда /status – повторная проверка платежей и вывод текущего статуса
 */
"""

from __future__ import annotations

from aiogram import Router, Bot
from aiogram.filters import Command
from aiogram.types import Message
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import User, UserStatus, Payment, PaymentStatus
from bot.services.payments import verify_payments

router = Router()


@router.message(Command("status"))
async def cmd_status(message: Message, session: AsyncSession, bot: Bot) -> None:
    telegram_id = str(message.from_user.id)

    result = await session.execute(select(User).where(User.telegram_id == telegram_id))
    user: User | None = result.scalar_one_or_none()
    if user is None:
        await message.answer("Вы ещё не зарегистрированы. Нажмите /start.")
        return

    if user.status == UserStatus.active:
        await message.answer("Ваш статус: <b>Активен</b>. Вы можете приглашать новых игроков.")
        return

    # Попробуем перепроверить платежи
    verified = await verify_payments(session, user_wallet=user.usdt_wallet, chain_id=0)
    if verified:
        user.status = UserStatus.active
        await session.commit()
        await message.answer("Оплата подтверждена! Ваш статус обновлён на <b>Активен</b>.")
    else:
        # Сколько платежей ещё ждут?
        pending_count = await session.scalar(
            select(func.count()).select_from(Payment).where(
                Payment.from_wallet == user.usdt_wallet,
                Payment.chain_id == 0,
                Payment.status == PaymentStatus.waiting,
            )
        )
        await message.answer(
            f"Оплата пока не найдена. Ожидаем подтверждение для {pending_count} адресов."
        ) 