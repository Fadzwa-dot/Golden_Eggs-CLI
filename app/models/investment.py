from __future__ import annotations
from app.database import db

class Investment(db.Model):
    __tablename__ = "investment"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    portfolio_id = db.Column(db.Integer, db.ForeignKey("portfolio.id"), nullable=False)
    security_ticker = db.Column(db.String, db.ForeignKey("security.ticker"), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    purchase_price = db.Column(db.Float, nullable=False)

    portfolio = db.relationship("Portfolio", back_populates="investments")
    security = db.relationship("Security", back_populates="investments")
