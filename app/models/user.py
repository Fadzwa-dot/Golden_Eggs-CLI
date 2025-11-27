from __future__ import annotations
from typing import TYPE_CHECKING
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Float
from app.db import Base

if TYPE_CHECKING:
    from .portfolio import Portfolio

class User(Base):
    __tablename__ = "user"

    username: Mapped[str] = mapped_column(String(50), primary_key=True)
    first_name: Mapped[str] = mapped_column(String(50), nullable=False)
    last_name: Mapped[str] = mapped_column(String(50), nullable=False)
    password: Mapped[str] = mapped_column(String(128), nullable=False)
    balance: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    role: Mapped[str] = mapped_column(String(20), default="customer", nullable=False)

    portfolios: Mapped[list["Portfolio"]] = relationship(
        "Portfolio",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin"
    )
