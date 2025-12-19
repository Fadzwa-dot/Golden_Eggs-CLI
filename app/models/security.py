from __future__ import annotations
from app.database import db

class Security(db.Model):
    __tablename__ = "security"

    ticker = db.Column(db.String(20), primary_key=True)
    # Map attribute `name` to existing DB column `issuer` for compatibility
    name = db.Column("issuer", db.String(200), nullable=False)
    price = db.Column(db.Float, nullable=False)

    investments = db.relationship("Investment", back_populates="security")
    transactions = db.relationship("Transaction", back_populates="security")
