from __future__ import annotations
from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db import Base

class Portfolio(Base):
    __tablename__ = "portfolio"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(String(255), nullable=True)
    # Reference user by username (string primary key)
    owner_username: Mapped[str] = mapped_column(ForeignKey("user.username"), nullable=False)

    owner = relationship("User", back_populates="portfolios")
    investments = relationship("Investment", back_populates="portfolio")
