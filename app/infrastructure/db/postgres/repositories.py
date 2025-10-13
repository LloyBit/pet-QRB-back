from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError
from app.infrastructure.db.postgres.schemas import Transactions  


class PaymentRepository:

    def __init__(self, db_helper):
        self.db = db_helper  # SyncDatabaseHelper

    def migrate_payment(self, tx_data: dict) -> bool:
        """
        Переносит транзакцию из Redis в PostgreSQL.
        tx_data — словарь, содержащий payment_id, user_id, tariff_id, amount, status, created_at.
        Возвращает True при успехе.
        """
        with self.db.transaction() as session:
            try:
                tx = Transactions(
                    payment_id=tx_data["payment_id"],
                    user_id=tx_data["user_id"],
                    tariff_id=tx_data["tariff_id"],
                    amount=tx_data["amount"],
                    status=tx_data.get("status", "pending"),
                    created_at=datetime.fromisoformat(tx_data["created_at"])
                    if isinstance(tx_data["created_at"], str)
                    else tx_data["created_at"],
                )
                session.add(tx)
                return True
            except SQLAlchemyError as e:
                session.rollback()
                return False
