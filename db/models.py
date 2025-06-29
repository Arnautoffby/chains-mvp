"""
/**
 * @file: models.py
 * @description: Базовые модели SQLAlchemy для Telegram-бота Chains
 * @dependencies: base.py, SQLAlchemy
 * @created: 2025-06-28
 */
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import List, Optional

from sqlalchemy import (
    DateTime,
    Enum as SqlEnum,
    ForeignKey,
    Integer,
    Numeric,
    String,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class UserStatus(str, Enum):
    pending = "ожидает оплату"
    active = "активен"
    blocked = "заблокирован"


class ChainStatus(str, Enum):
    active = "активна"
    finished = "завершена"


class MembershipRole(str, Enum):
    organizer = "организатор"
    participant = "участник"
    invitee = "приглашённый"


class MembershipStatus(str, Enum):
    pending = "ожидает оплату"
    active = "активен"
    removed = "удален"
    winner = "победитель"


class PaymentStatus(str, Enum):
    waiting = "ожидание"
    confirmed = "подтвержден"
    rejected = "отклонен"


class SlotStatus(str, Enum):
    pending = "ожидание оплаты"
    active = "активен"
    expired = "просрочен"
    removed = "удален"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    telegram_id: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    usdt_wallet: Mapped[str] = mapped_column(String(64), nullable=False)
    status: Mapped[UserStatus] = mapped_column(SqlEnum(UserStatus), default=UserStatus.pending)
    date_joined: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    memberships: Mapped[List["UserChainMembership"]] = relationship(back_populates="user")


class Chain(Base):
    __tablename__ = "chains"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    entry_fee: Mapped[Numeric] = mapped_column(Numeric(10, 2), nullable=False)
    max_slots: Mapped[int] = mapped_column(Integer, nullable=False, default=3)
    status: Mapped[ChainStatus] = mapped_column(SqlEnum(ChainStatus), default=ChainStatus.active)
    date_created: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    memberships: Mapped[List["UserChainMembership"]] = relationship(back_populates="chain")


class UserChainMembership(Base):
    __tablename__ = "user_chain_memberships"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    chain_id: Mapped[int] = mapped_column(ForeignKey("chains.id"), nullable=False)

    role: Mapped[MembershipRole] = mapped_column(SqlEnum(MembershipRole), default=MembershipRole.participant)
    current_level: Mapped[int] = mapped_column(Integer, default=1)
    status: Mapped[MembershipStatus] = mapped_column(SqlEnum(MembershipStatus), default=MembershipStatus.pending)

    invite_link: Mapped[Optional[str]] = mapped_column(String(255))
    invited_by: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"))

    invited_users: Mapped[Optional[List[int]]] = mapped_column(JSONB, default=list)
    payments: Mapped[Optional[List[int]]] = mapped_column(JSONB, default=list)

    join_time: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    slots_total: Mapped[int] = mapped_column(Integer, default=3)
    slots_filled: Mapped[int] = mapped_column(Integer, default=0)

    slots: Mapped[List["Slot"]] = relationship(back_populates="owner_membership")

    user: Mapped["User"] = relationship(back_populates="memberships", foreign_keys=[user_id])
    chain: Mapped["Chain"] = relationship(back_populates="memberships", foreign_keys=[chain_id])


class Payment(Base):
    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    chain_id: Mapped[int] = mapped_column(ForeignKey("chains.id"), nullable=False)

    from_wallet: Mapped[str] = mapped_column(String(64), nullable=False)
    to_wallet: Mapped[str] = mapped_column(String(64), nullable=False)
    amount: Mapped[Numeric] = mapped_column(Numeric(10, 2), nullable=False)
    txid: Mapped[str] = mapped_column(String(128), nullable=False)
    status: Mapped[PaymentStatus] = mapped_column(SqlEnum(PaymentStatus), default=PaymentStatus.waiting)
    date_sent: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Slot(Base):
    __tablename__ = "slots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    owner_membership_id: Mapped[int] = mapped_column(ForeignKey("user_chain_memberships.id"), nullable=False)
    invited_user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"))
    status: Mapped[SlotStatus] = mapped_column(SqlEnum(SlotStatus), default=SlotStatus.pending)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    paid_at: Mapped[Optional[datetime]] = mapped_column(DateTime)

    owner_membership: Mapped["UserChainMembership"] = relationship(back_populates="slots") 