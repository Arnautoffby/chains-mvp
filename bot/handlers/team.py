"""
/**
 * @file: team.py
 * @description: Команды /myteam и управление слотами (удаление неактивных)
 */
"""

from __future__ import annotations

from aiogram import Router, Bot
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import User, UserChainMembership, Slot, SlotStatus

router = Router()


def _slot_emoji(status: SlotStatus) -> str:
    return {
        SlotStatus.pending: "⌛",
        SlotStatus.active: "✅",
        SlotStatus.expired: "⚠️",
        SlotStatus.removed: "❌",
    }[status]


@router.message(Command("myteam"))
async def cmd_myteam(message: Message, session: AsyncSession, bot: Bot) -> None:
    telegram_id = str(message.from_user.id)
    res = await session.execute(select(User).where(User.telegram_id == telegram_id))
    user: User | None = res.scalar_one_or_none()
    if not user:
        await message.answer("Сначала зарегистрируйтесь /start")
        return

    # Для MVP берём первую membership
    m_res = await session.execute(select(UserChainMembership).where(UserChainMembership.user_id == user.id))
    membership: UserChainMembership | None = m_res.scalar_one_or_none()
    if not membership:
        await message.answer("Нет данных о цепи.")
        return

    s_res = await session.execute(select(Slot).where(Slot.owner_membership_id == membership.id))
    slots = s_res.scalars().all()

    lines = []
    buttons = []
    for s in slots:
        emoji = _slot_emoji(s.status)
        if s.status in {SlotStatus.pending, SlotStatus.expired}:
            # кнопка удалить
            buttons.append([InlineKeyboardButton(text=f"Удалить слот {s.id}", callback_data=f"remove_slot:{s.id}")])
        invited = f"userid={s.invited_user_id}" if s.invited_user_id else "пусто"
        lines.append(f"{emoji} Слот {s.id}: {invited}")

    kb = InlineKeyboardMarkup(inline_keyboard=buttons) if buttons else None
    await message.answer("\n".join(lines) or "Слоты не созданы", reply_markup=kb)


@router.callback_query(lambda c: c.data and c.data.startswith("remove_slot:"))
async def cb_remove_slot(callback: CallbackQuery, session: AsyncSession) -> None:
    slot_id = int(callback.data.split(":")[1])
    slot = await session.get(Slot, slot_id)
    if not slot or slot.status not in {SlotStatus.pending, SlotStatus.expired}:
        await callback.answer("Нельзя удалить этот слот", show_alert=True)
        return

    slot.status = SlotStatus.removed
    await session.commit()
    await callback.answer("Слот удалён")
    await callback.message.delete() 