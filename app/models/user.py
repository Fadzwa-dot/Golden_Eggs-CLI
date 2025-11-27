from __future__ import annotations
from sqlalchemy import String, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db import Base

class User(Base):
    __tablename__ = "user"

    # Use username as the primary key to match legacy domain usage
    username: Mapped[str] = mapped_column(String(100), primary_key=True)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    balance: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    role: Mapped[str] = mapped_column(String(50), nullable=False, default="customer")

    portfolios = relationship("Portfolio", back_populates="owner")
    transactions = relationship("Transaction", back_populates="user")
