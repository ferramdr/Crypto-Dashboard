"""
Database models for the Crypto Investment application
"""
from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime
from database import Base


class Investment(Base):
    """
    Investment table to track cryptocurrency purchases
    """
    __tablename__ = "investments"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    coin_name = Column(String(100), nullable=False, index=True)
    amount = Column(Float, nullable=False)
    purchase_price_usd = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<Investment(id={self.id}, coin={self.coin_name}, amount={self.amount}, price=${self.purchase_price_usd})>"
