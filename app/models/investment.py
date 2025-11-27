from __future__ import annotations
from typing import TYPE_CHECKING
from sqlalchemy import Float, Integer, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db import Base

if TYPE_CHECKING:
    from .portfolio import Portfolio
    from .security import Security

class Investment(Base):
    __tablename__ = "investment"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    portfolio_id: Mapped[int] = mapped_column(ForeignKey("portfolio.id"), nullable=False)
    security_ticker: Mapped[str] = mapped_column(ForeignKey("security.ticker"), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    purchase_price: Mapped[float] = mapped_column(Float, nullable=False)

    portfolio: Mapped["Portfolio"] = relationship("Portfolio", back_populates="investments")
    security: Mapped["Security"] = relationship("Security", back_populates="investments")
