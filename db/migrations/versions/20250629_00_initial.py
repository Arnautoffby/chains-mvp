"""initial schema

Revision ID: 20250629_00
Revises:
Create Date: 2025-06-29
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '20250629_00'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # users
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('telegram_id', sa.String(length=64), nullable=False, unique=True),
        sa.Column('usdt_wallet', sa.String(length=64), nullable=False),
        sa.Column('status', sa.Enum('ожидает оплату', 'активен', 'заблокирован', name='userstatus'), nullable=False, server_default='ожидает оплату'),
        sa.Column('date_joined', sa.DateTime(), nullable=False),
    )

    op.create_table(
        'chains',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('created_by', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('entry_fee', sa.Numeric(10, 2), nullable=False),
        sa.Column('max_slots', sa.Integer(), nullable=False, server_default='3'),
        sa.Column('status', sa.Enum('активна', 'завершена', name='chainstatus'), nullable=False, server_default='активна'),
        sa.Column('date_created', sa.DateTime(), nullable=False),
    )

    op.create_table(
        'user_chain_memberships',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('chain_id', sa.Integer(), sa.ForeignKey('chains.id'), nullable=False),
        sa.Column('role', sa.Enum('организатор', 'участник', 'приглашённый', name='membershiprole'), nullable=False, server_default='участник'),
        sa.Column('current_level', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('status', sa.Enum('ожидает оплату', 'активен', 'удален', 'победитель', name='membershipstatus'), nullable=False, server_default='ожидает оплату'),
        sa.Column('invite_link', sa.String(length=255)),
        sa.Column('invited_by', sa.Integer(), sa.ForeignKey('users.id')),
        sa.Column('invited_users', postgresql.JSONB(astext_type=sa.Text())),
        sa.Column('payments', postgresql.JSONB(astext_type=sa.Text())),
        sa.Column('join_time', sa.DateTime(), nullable=False),
        sa.Column('slots_total', sa.Integer(), nullable=False, server_default='3'),
        sa.Column('slots_filled', sa.Integer(), nullable=False, server_default='0'),
    )

    op.create_table(
        'payments',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('chain_id', sa.Integer(), sa.ForeignKey('chains.id'), nullable=False),
        sa.Column('from_wallet', sa.String(length=64), nullable=False),
        sa.Column('to_wallet', sa.String(length=64), nullable=False),
        sa.Column('amount', sa.Numeric(10, 2), nullable=False),
        sa.Column('txid', sa.String(length=128), nullable=False),
        sa.Column('status', sa.Enum('ожидание', 'подтвержден', 'отклонен', name='paymentstatus'), nullable=False, server_default='ожидание'),
        sa.Column('date_sent', sa.DateTime(), nullable=False),
    )

    op.create_table(
        'slots',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('owner_membership_id', sa.Integer(), sa.ForeignKey('user_chain_memberships.id'), nullable=False),
        sa.Column('invited_user_id', sa.Integer(), sa.ForeignKey('users.id')),
        sa.Column('status', sa.Enum('pending', 'active', 'expired', 'removed', name='slotstatus'), nullable=False, server_default='pending'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('paid_at', sa.DateTime()),
    )


def downgrade() -> None:
    op.drop_table('slots')
    op.drop_table('payments')
    op.drop_table('user_chain_memberships')
    op.drop_table('chains')
    op.drop_table('users') 