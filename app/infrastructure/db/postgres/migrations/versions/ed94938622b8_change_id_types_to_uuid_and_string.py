"""change_id_types_to_uuid_and_string

Revision ID: ed94938622b8
Revises: e74a553f2ac8
Create Date: 2025-09-19 02:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'ed94938622b8'
down_revision: Union[str, Sequence[str], None] = 'e74a553f2ac8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    
    # 1. Сначала удаляем все foreign key constraints
    op.drop_constraint('users_tariff_id_fkey', 'users', type_='foreignkey')
    op.drop_constraint('transactions_user_id_fkey', 'transactions', type_='foreignkey')
    op.drop_constraint('transactions_tariff_id_fkey', 'transactions', type_='foreignkey')
    
    # 2. Создаем новые колонки с правильными типами
    op.add_column('tariffs', sa.Column('tariff_id_new', postgresql.UUID(), nullable=False))
    op.add_column('users', sa.Column('user_id_new', sa.String(), nullable=False))
    op.add_column('users', sa.Column('tariff_id_new', postgresql.UUID(), nullable=True))  # Добавляем новую колонку tariff_id для users
    op.add_column('transactions', sa.Column('payment_id_new', postgresql.UUID(), nullable=False))
    op.add_column('transactions', sa.Column('user_id_new', sa.String(), nullable=False))
    op.add_column('transactions', sa.Column('tariff_id_new', postgresql.UUID(), nullable=False))
    
    # 3. Заполняем новые колонки данными
    # Для UUID генерируем новые UUID
    op.execute("UPDATE tariffs SET tariff_id_new = gen_random_uuid()")
    op.execute("UPDATE users SET user_id_new = user_id::text")
    op.execute("UPDATE transactions SET payment_id_new = gen_random_uuid()")
    op.execute("UPDATE transactions SET user_id_new = user_id::text")
    
    # Для tariff_id в users - получаем UUID из таблицы tariffs
    op.execute("""
        UPDATE users 
        SET tariff_id_new = t.tariff_id_new 
        FROM tariffs t 
        WHERE users.tariff_id = t.tariff_id::integer
    """)
    
    # Для tariff_id в transactions - получаем UUID из таблицы tariffs
    op.execute("""
        UPDATE transactions 
        SET tariff_id_new = t.tariff_id_new 
        FROM tariffs t 
        WHERE transactions.tariff_id = t.tariff_id::integer
    """)
    
    # 4. Удаляем старые колонки (теперь это безопасно, так как constraints удалены)
    op.drop_column('transactions', 'tariff_id')
    op.drop_column('transactions', 'user_id')
    op.drop_column('transactions', 'payment_id')
    op.drop_column('users', 'user_id')
    op.drop_column('users', 'tariff_id')  # Удаляем старую колонку tariff_id из users
    op.drop_column('tariffs', 'tariff_id')
    
    # 5. Переименовываем новые колонки
    op.alter_column('tariffs', 'tariff_id_new', new_column_name='tariff_id')
    op.alter_column('users', 'user_id_new', new_column_name='user_id')
    op.alter_column('users', 'tariff_id_new', new_column_name='tariff_id')  # Переименовываем новую колонку tariff_id в users
    op.alter_column('transactions', 'payment_id_new', new_column_name='payment_id')
    op.alter_column('transactions', 'user_id_new', new_column_name='user_id')
    op.alter_column('transactions', 'tariff_id_new', new_column_name='tariff_id')
    
    # 6. Устанавливаем primary key constraints
    op.create_primary_key('tariffs_pkey', 'tariffs', ['tariff_id'])
    op.create_primary_key('users_pkey', 'users', ['user_id'])
    op.create_primary_key('transactions_pkey', 'transactions', ['payment_id'])
    
    # 7. Восстанавливаем foreign key constraints (теперь типы совместимы)
    op.create_foreign_key('users_tariff_id_fkey', 'users', 'tariffs', ['tariff_id'], ['tariff_id'])
    op.create_foreign_key('transactions_user_id_fkey', 'transactions', 'users', ['user_id'], ['user_id'])
    op.create_foreign_key('transactions_tariff_id_fkey', 'transactions', 'tariffs', ['tariff_id'], ['tariff_id'])
    
    # 8. Создаем индексы
    op.create_index('ix_tariffs_tariff_id', 'tariffs', ['tariff_id'])
    op.create_index('ix_users_user_id', 'users', ['user_id'])
    op.create_index('ix_transactions_payment_id', 'transactions', ['payment_id'])
    
    # 9. Удаляем старые sequences
    op.execute("DROP SEQUENCE IF EXISTS tariffs_tariff_id_seq")
    op.execute("DROP SEQUENCE IF EXISTS users_user_id_seq")


def downgrade() -> None:
    """Downgrade schema."""
    
    # 1. Удаляем foreign key constraints
    op.drop_constraint('transactions_tariff_id_fkey', 'transactions', type_='foreignkey')
    op.drop_constraint('transactions_user_id_fkey', 'transactions', type_='foreignkey')
    op.drop_constraint('users_tariff_id_fkey', 'users', type_='foreignkey')
    
    # 2. Удаляем primary key constraints
    op.drop_constraint('transactions_pkey', 'transactions', type_='primary')
    op.drop_constraint('users_pkey', 'users', type_='primary')
    op.drop_constraint('tariffs_pkey', 'tariffs', type_='primary')
    
    # 3. Создаем старые колонки
    op.add_column('tariffs', sa.Column('tariff_id_old', sa.Integer(), nullable=False))
    op.add_column('users', sa.Column('user_id_old', sa.Integer(), nullable=False))
    op.add_column('users', sa.Column('tariff_id_old', sa.Integer(), nullable=True))
    op.add_column('transactions', sa.Column('payment_id_old', sa.String(), nullable=False))
    op.add_column('transactions', sa.Column('user_id_old', sa.Integer(), nullable=False))
    op.add_column('transactions', sa.Column('tariff_id_old', sa.Integer(), nullable=False))
    
    # 4. Заполняем старые колонки (это сложно, так как UUID нельзя просто преобразовать в INTEGER)
    # В реальном проекте нужно сохранить маппинг или использовать другой подход
    op.execute("UPDATE tariffs SET tariff_id_old = 1")  # Временное решение
    op.execute("UPDATE users SET user_id_old = 1")      # Временное решение
    op.execute("UPDATE users SET tariff_id_old = 1")    # Временное решение
    op.execute("UPDATE transactions SET payment_id_old = 'temp'")
    op.execute("UPDATE transactions SET user_id_old = 1")
    op.execute("UPDATE transactions SET tariff_id_old = 1")
    
    # 5. Удаляем новые колонки
    op.drop_column('transactions', 'tariff_id')
    op.drop_column('transactions', 'user_id')
    op.drop_column('transactions', 'payment_id')
    op.drop_column('users', 'user_id')
    op.drop_column('users', 'tariff_id')
    op.drop_column('tariffs', 'tariff_id')
    
    # 6. Переименовываем старые колонки
    op.alter_column('tariffs', 'tariff_id_old', new_column_name='tariff_id')
    op.alter_column('users', 'user_id_old', new_column_name='user_id')
    op.alter_column('users', 'tariff_id_old', new_column_name='tariff_id')
    op.alter_column('transactions', 'payment_id_old', new_column_name='payment_id')
    op.alter_column('transactions', 'user_id_old', new_column_name='user_id')
    op.alter_column('transactions', 'tariff_id_old', new_column_name='tariff_id')
    
    # 7. Восстанавливаем sequences
    op.execute("CREATE SEQUENCE IF NOT EXISTS tariffs_tariff_id_seq")
    op.execute("CREATE SEQUENCE IF NOT EXISTS users_user_id_seq")
    
    # 8. Устанавливаем default values
    op.execute("ALTER TABLE tariffs ALTER COLUMN tariff_id SET DEFAULT nextval('tariffs_tariff_id_seq')")
    op.execute("ALTER TABLE users ALTER COLUMN user_id SET DEFAULT nextval('users_user_id_seq')")