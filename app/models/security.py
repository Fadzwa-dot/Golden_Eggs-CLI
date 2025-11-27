from __future__ import annotations
from typing import TYPE_CHECKING
from sqlalchemy import String, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db import Base

if TYPE_CHECKING:
    from .investment import Investment

class Security(Base):
    __tablename__ = "security"

    ticker: Mapped[str] = mapped_column(String(10), primary_key=True)
    issuer: Mapped[str] = mapped_column(String(100), nullable=False)
    price: Mapped[float] = mapped_column(Float, nullable=False)

    investments: Mapped[list["Investment"]] = relationship(
        "Investment",
        back_populates="security",
        cascade="all, delete-orphan",
        lazy="selectin"
    )
