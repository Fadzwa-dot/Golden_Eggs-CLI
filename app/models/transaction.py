from __future__ import annotations
from datetime import datetime, timezone
from sqlalchemy import Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db import Base

class Transaction(Base):
    __tablename__ = "transaction"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    # user_id references user.username (string primary key)
    user_id: Mapped[str] = mapped_column(ForeignKey("user.username"), nullable=False)
    # use 'security_id' column name to match existing DB and service code
    security_id: Mapped[str] = mapped_column(ForeignKey("security.ticker"), nullable=False)
    transaction_type: Mapped[str] = mapped_column(String(10), nullable=False)  # BUY/SELL
    portfolio_id: Mapped[int] = mapped_column(ForeignKey("portfolio.id"), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    # Use timezone-aware UTC timestamps to avoid deprecation warnings
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="transactions")
    security = relationship("Security", back_populates="transactions")
