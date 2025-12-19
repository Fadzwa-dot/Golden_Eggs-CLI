from __future__ import annotations
from app.database import db

class Portfolio(db.Model):
    __tablename__ = "portfolio"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255), nullable=True)
    # Reference user by username (string primary key)
    owner_username = db.Column(db.String, db.ForeignKey("user.username"), nullable=False)

    owner = db.relationship("User", back_populates="portfolios")
    investments = db.relationship("Investment", back_populates="portfolio")
