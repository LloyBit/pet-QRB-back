from datetime import datetime, timezone

from dateutil.relativedelta import relativedelta
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import declarative_base, relationship 

Base = declarative_base()

class Users(Base):
    __tablename__ = 'users'

    user_id = Column(Integer, primary_key=True, index=True)
    tariff_id = Column(ForeignKey("tariffs.tariff_id"), nullable=True)  
    tariff_expires_at = Column(DateTime, nullable=True)

    # связи
    tariff = relationship("Tariffs", back_populates="users")
    transactions = relationship("Transactions", back_populates="user")

class Tariffs(Base):
    __tablename__ = 'tariffs'

    tariff_id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    price = Column(Integer, nullable=False)
    features = Column(String, nullable=False)
    
    # флажок активности тарифа, чтобы можно было его деактивировать а затем отключить
    is_active = Column(Boolean, default=True, nullable=False)
    
    # связи
    users = relationship("Users", back_populates="tariff")
    transactions = relationship("Transactions", back_populates="tariff")

class Transactions(Base):
    __tablename__ = 'transactions'

    # Изменяем payment_id на String для поддержки UUID
    payment_id = Column(String, primary_key=True, index=True)
    user_id = Column(ForeignKey("users.user_id"), nullable=False)
    tariff_id = Column(ForeignKey("tariffs.tariff_id"), nullable=False)
    amount = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    expired_at = Column(DateTime, default=lambda: datetime.now(timezone.utc) + relativedelta(months=+1))
    
    # связи
    user = relationship("Users", back_populates="transactions")
    tariff = relationship("Tariffs", back_populates="transactions")
