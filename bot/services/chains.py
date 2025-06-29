"""
/**
 * @file: chains.py
 * @description: Сервис управления слотами и уровнями цепи
 */
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import List

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import (
    UserChainMembership,
    Slot,
    SlotStatus,
)

logger = logging.getLogger(__name__)

SLOT_TIMEOUT_HOURS = 24


async def create_initial_slots(session: AsyncSession, membership: UserChainMembership) -> List[Slot]:
    """Создаёт пустые слоты для организатора."""

    slots = [
        Slot(owner_membership_id=membership.id) for _ in range(membership.slots_total)
    ]
    session.add_all(slots)
    await session.flush()
    return slots


async def reserve_slot(session: AsyncSession, owner_membership_id: int, invited_user_id: int) -> Slot | None:
    """Резервирует свободный слот для invited_user."""

    result = await session.execute(
        select(Slot)
        .where(
            Slot.owner_membership_id == owner_membership_id,
            Slot.status == SlotStatus.pending,
            Slot.invited_user_id.is_(None),
        )
        .limit(1)
    )
    slot: Slot | None = result.scalar_one_or_none()
    if slot is None:
        return None

    slot.invited_user_id = invited_user_id
    slot.created_at = datetime.utcnow()
    await session.flush()
    return slot


async def activate_slot(session: AsyncSession, invited_user_membership: UserChainMembership) -> None:
    """Помечает слот активным и увеличивает счётчик у организатора."""

    # найдём слот по invited_user_id
    result = await session.execute(
        select(Slot).where(
            Slot.invited_user_id == invited_user_membership.user_id,
            Slot.status == SlotStatus.pending,
        )
    )
    slot: Slot | None = result.scalar_one_or_none()
    if slot is None:
        return

    slot.status = SlotStatus.active
    slot.paid_at = datetime.utcnow()

    # Обновим счётчик
    await session.execute(
        update(UserChainMembership)
        .where(UserChainMembership.id == slot.owner_membership_id)
        .values(slots_filled=UserChainMembership.slots_filled + 1)
    )


async def expire_old_slots(session: AsyncSession) -> int:
    """Помечает слоты pending, созданные >24ч назад, как expired."""

    threshold = datetime.utcnow() - timedelta(hours=SLOT_TIMEOUT_HOURS)
    result = await session.execute(
        select(Slot).where(
            Slot.status == SlotStatus.pending,
            Slot.created_at < threshold,
        )
    )
    slots: List[Slot] = result.scalars().all()
    for s in slots:
        s.status = SlotStatus.expired
    logger.info("Expired %s slots", len(slots))
    return len(slots) 