"""initial tables

Revision ID: 8d887ad81982
Revises: 29a6c6ff8388
Create Date: 2025-09-28 15:27:37.831483

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8d887ad81982'
down_revision: Union[str, Sequence[str], None] = '29a6c6ff8388'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Удаляем FK
    op.drop_constraint('transactions_user_id_fkey', 'transactions', type_='foreignkey')
    
    # 2. Меняем типы колонок
    op.alter_column(
        'users',
        'user_id',
        existing_type=sa.VARCHAR(),
        type_=sa.BigInteger(),  # или sa.Integer()
        existing_nullable=False,
        postgresql_using='user_id::bigint'
    )
    op.alter_column(
        'transactions',
        'user_id',
        existing_type=sa.VARCHAR(),
        type_=sa.BigInteger(),
        existing_nullable=False,
        postgresql_using='user_id::bigint'
    )
    
    # 3. Восстанавливаем FK
    op.create_foreign_key(
        'transactions_user_id_fkey',
        source_table='transactions',
        referent_table='users',
        local_cols=['user_id'],
        remote_cols=['user_id']
    )


def downgrade() -> None:
    op.drop_constraint('transactions_user_id_fkey', 'transactions', type_='foreignkey')
    
    op.alter_column(
        'transactions',
        'user_id',
        existing_type=sa.BigInteger(),
        type_=sa.VARCHAR(),
        existing_nullable=False,
        postgresql_using='user_id::text'
    )
    op.alter_column(
        'users',
        'user_id',
        existing_type=sa.BigInteger(),
        type_=sa.VARCHAR(),
        existing_nullable=False,
        postgresql_using='user_id::text'
    )
    
    op.create_foreign_key(
        'transactions_user_id_fkey',
        source_table='transactions',
        referent_table='users',
        local_cols=['user_id'],
        remote_cols=['user_id']
    )
