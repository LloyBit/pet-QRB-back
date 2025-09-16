"""ORM схемы для Postgres"""
from datetime import datetime

from dateutil.relativedelta import relativedelta
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, UUID
from sqlalchemy.orm import relationship 

# Импортируем Base из database.py вместо создания нового
from app.infrastructure.db.postgres.database import db_helper

class Users(db_helper.Base):
    __tablename__ = 'users'

    user_id = Column(Integer, primary_key=True, index=True) # TODO: change to UUID
    tariff_id = Column(ForeignKey("tariffs.tariff_id"), nullable=True)  
    tariff_expires_at = Column(DateTime, nullable=True)

    # связи
    tariff = relationship("Tariffs", back_populates="users")
    transactions = relationship("Transactions", back_populates="user")

class Tariffs(db_helper.Base):
    __tablename__ = 'tariffs'

    tariff_id = Column(Integer, primary_key=True, index=True) # TODO: change to UUID
    name = Column(String, unique=True, nullable=False)
    price = Column(Integer, nullable=False)
    features = Column(String, nullable=False)
    # флажок активности тарифа, чтобы можно было его деактивировать а затем отключить
    is_active = Column(Boolean, default=True, nullable=False)
    
    # связи
    users = relationship("Users", back_populates="tariff")
    transactions = relationship("Transactions", back_populates="tariff")

class Transactions(db_helper.Base):
    __tablename__ = 'transactions'

    # Изменяем payment_id на String для поддержки UUID
    payment_id = Column(UUID, primary_key=True, index=True)
    user_id = Column(ForeignKey("users.user_id"), nullable=False) # TODO: change to UUID
    tariff_id = Column(ForeignKey("tariffs.tariff_id"), nullable=False) # TODO: change to UUID
    amount = Column(Integer, nullable=False)
    status = Column(String, default="pending", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    expired_at = Column(DateTime, default=lambda: datetime.utcnow() + relativedelta(months=+1))
    
    # связи
    user = relationship("Users", back_populates="transactions")
    tariff = relationship("Tariffs", back_populates="transactions")
