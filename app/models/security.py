from __future__ import annotations
from sqlalchemy import String, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db import Base

class Security(Base):
    __tablename__ = "security"

    ticker: Mapped[str] = mapped_column(String(20), primary_key=True)
    # The database column was previously named `issuer` in some environments.
    # Map the `name` attribute to the existing `issuer` column to remain
    # compatible with older schemas without forcing an immediate migration.
    name: Mapped[str] = mapped_column("issuer", String(200), nullable=False)
    price: Mapped[float] = mapped_column(Float, nullable=False)

    investments = relationship("Investment", back_populates="security")
    transactions = relationship("Transaction", back_populates="security")
