"""
/**
 * @file: payments.py
 * @description: Логика создания и проверки платежей в системе
 * @dependencies: db.models, blockchain
 * @created: 2025-06-29
 */
"""

from __future__ import annotations

from typing import List

from sqlalchemy.ext.asyncio import AsyncSession

from db.models import Payment, PaymentStatus
from bot.config import get_settings
from bot.services.blockchain import TronScanAPI

settings = get_settings()
api = TronScanAPI()


async def create_pending_payments(session: AsyncSession, chain_id: int, from_wallet: str) -> List[Payment]:
    """Создаёт записи Payment со статусом waiting для заданного пользователя.

    По MVP всегда использует фиксированный список адресов из конфигурации.
    """

    payments: List[Payment] = []
    for addr in settings.game.payment_addresses:
        payment = Payment(
            chain_id=chain_id,
            from_wallet=from_wallet,
            to_wallet=addr,
            amount=1.0,
            txid="",  # неизвестен до подтверждения
            status=PaymentStatus.waiting,
        )
        session.add(payment)
        payments.append(payment)

    await session.flush()
    return payments


async def verify_payments(session: AsyncSession, user_wallet: str, chain_id: int) -> bool:
    """Проверяет платежи и обновляет статусы."""

    # Получаем платежи по цепи
    result = await session.execute(
        Payment.__table__.select().where(
            Payment.chain_id == chain_id,
            Payment.from_wallet == user_wallet,
        )
    )
    payments = [Payment(**row) for row in result]

    addresses = [p.to_wallet for p in payments if p.status == PaymentStatus.waiting]
    if not addresses:
        return True  # уже подтверждено

    confirmed = await api.verify_payments(user_wallet, addresses)

    if confirmed:
        # simple mass update to confirmed
        await session.execute(
            Payment.__table__.update()
            .where(
                Payment.chain_id == chain_id,
                Payment.from_wallet == user_wallet,
            )
            .values(status=PaymentStatus.confirmed)
        )
        await session.commit()
    return confirmed 