from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError
from app.infrastructure.db.postgres.schemas import Transactions  
from app.infrastructure.db.postgres.database import AsyncDatabaseHelper
from sqlalchemy import select

class TransactionsRepository:
    def __init__(self, async_db_helper: AsyncDatabaseHelper):
        self.async_db = async_db_helper  
    
    async def create(self, tx_data: dict) -> Transactions:
        async with self.async_db.transaction() as session:
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
                return tx
            except SQLAlchemyError as e:
                session.rollback()
                return False

    async def find(self, payment_id):
        async with self.async_db.session_only() as session:
            query = select(Transactions).where(Transactions.payment_id == payment_id)
            result = await session.execute(query)
            tx = result.scalar_one_or_none() 
            return tx
