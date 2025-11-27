from __future__ import annotations
from typing import TYPE_CHECKING
from sqlalchemy import Integer, String, Float, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db import Base

if TYPE_CHECKING:
    from .user import User
    from .portfolio import Portfolio
    from .security import Security

class Transaction(Base):
    __tablename__ = "transaction"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("user.username"), nullable=False)
    portfolio_id: Mapped[int] = mapped_column(ForeignKey("portfolio.id"), nullable=False)
    security_id: Mapped[str] = mapped_column(ForeignKey("security.ticker"), nullable=False)
    transaction_type: Mapped[str] = mapped_column(String(10), nullable=False)  # "BUY" or "SELL"
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    timestamp: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now(), nullable=False)

    user: Mapped["User"] = relationship("User")
    portfolio: Mapped["Portfolio"] = relationship("Portfolio")
    security: Mapped["Security"] = relationship("Security")
