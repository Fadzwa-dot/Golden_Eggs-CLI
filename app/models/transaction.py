from __future__ import annotations
from datetime import datetime, timezone
from app.database import db

class Transaction(db.Model):
    __tablename__ = "transaction"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    # user_id references user.username (string primary key)
    user_id = db.Column(db.String, db.ForeignKey("user.username"), nullable=False)
    # use 'security_id' column name to match existing DB and service code
    security_id = db.Column(db.String, db.ForeignKey("security.ticker"), nullable=False)
    transaction_type = db.Column(db.String(10), nullable=False)  # BUY/SELL
    portfolio_id = db.Column(db.Integer, db.ForeignKey("portfolio.id"), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    # Use timezone-aware UTC timestamps to avoid deprecation warnings
    timestamp = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    user = db.relationship("User", back_populates="transactions")
    security = db.relationship("Security", back_populates="transactions")
