from __future__ import annotations
from app.database import db

class User(db.Model):
    __tablename__ = "user"

    # Use username as the primary key to match legacy domain usage
    username = db.Column(db.String(100), primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    balance = db.Column(db.Float, nullable=False, default=0.0)
    role = db.Column(db.String(50), nullable=False, default="customer")

    portfolios = db.relationship("Portfolio", back_populates="owner")
    transactions = db.relationship("Transaction", back_populates="user")
