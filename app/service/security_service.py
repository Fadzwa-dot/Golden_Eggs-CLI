# app/service/security_service.py
from typing import List
from app.database import db
from app.models.security import Security
from app.models.portfolio import Portfolio
from app.models.user import User
from app.models.investment import Investment
from app.models.transaction import Transaction
from app.service.exceptions import NotFoundError, ValidationError

class SecurityService:
    """
    Simple service to expose securities stored in the top-level `db` module.
    Assumes `db.securities` is a dict mapping ticker -> Security.
    """
    def __init__(self) -> None:
        pass

    def log_transaction(self, user_id, portfolio_id, security_id, transaction_type, quantity, price):
        transaction = Transaction(
            user_id=user_id,
            portfolio_id=portfolio_id,
            security_id=security_id,
            transaction_type=transaction_type,
            quantity=quantity,
            price=price
        )
        db.session.add(transaction)
        db.session.commit()

    def list_securities(self) -> List[Security]:
        return db.session.query(Security).all()

    def get_security(self, ticker: str) -> Security:
        sec = db.session.query(Security).filter_by(ticker=ticker).first()
        if not sec:
            raise NotFoundError(f"Ticker '{ticker}' not found")
        return sec

    def buy_security(self, username: str, ticker: str, quantity: int, portfolio_id: int) -> None:
        if quantity <= 0:
            raise ValidationError("Quantity must be positive.")
        user = db.session.query(User).filter_by(username=username).first()
        if not user:
            raise NotFoundError(f"User '{username}' not found.")
        if user.role != "customer":
            raise ValidationError("Only customers can buy securities.")
        portfolio = db.session.query(Portfolio).filter_by(owner_username=username, id=portfolio_id).first()
        if not portfolio:
            raise NotFoundError(f"Portfolio with ID '{portfolio_id}' not found for user '{username}'.")
        security = db.session.query(Security).filter_by(ticker=ticker).first()
        if not security:
            raise NotFoundError(f"Security '{ticker}' not found in the marketplace.")
        cost = security.price * quantity
        if cost > user.balance:
            raise ValidationError("Insufficient balance to buy security.")
        user.balance -= cost
        existing = db.session.query(Investment).filter_by(portfolio_id=portfolio_id, security_ticker=ticker).first()
        if existing:
            existing.quantity += quantity
            existing.purchase_price = security.price
        else:
            investment = Investment(portfolio_id=portfolio_id, security_ticker=ticker, quantity=quantity, purchase_price=security.price)
            db.session.add(investment)
        db.session.commit()
        self.log_transaction(username, portfolio_id, ticker, "BUY", quantity, security.price)

    def sell_security(self, username: str, ticker: str, quantity: int, portfolio_id: int) -> None:
        if quantity <= 0:
            raise ValidationError("Quantity must be positive.")
        user = db.session.query(User).filter_by(username=username).first()
        if not user:
            raise NotFoundError(f"User '{username}' not found.")
        if user.role != "customer":
            raise ValidationError("Only customers can sell securities.")
        portfolio = db.session.query(Portfolio).filter_by(owner_username=username, id=portfolio_id).first()
        if not portfolio:
            raise NotFoundError(f"Portfolio with ID '{portfolio_id}' not found for user '{username}'.")
        investment = db.session.query(Investment).filter_by(portfolio_id=portfolio_id, security_ticker=ticker).first()
        if not investment:
            raise NotFoundError(f"Security '{ticker}' not found in portfolio '{portfolio.name}'.")
        security = db.session.query(Security).filter_by(ticker=ticker).first()
        if not security:
            raise NotFoundError(f"Security '{ticker}' not found in the marketplace.")
        if quantity > investment.quantity:
            raise ValidationError("Not enough shares to sell.")
        proceeds = quantity * security.price
        investment.quantity -= quantity
        if investment.quantity == 0:
            db.session.delete(investment)
        user.balance += proceeds
        db.session.commit()
        self.log_transaction(username, portfolio_id, ticker, "SELL", quantity, security.price)
    def get_all_transactions(self):
        return db.session.query(Transaction).order_by(Transaction.timestamp.desc()).all()

    def get_transactions_by_user(self, username: str):
        return db.session.query(Transaction).filter_by(user_id=username).order_by(Transaction.timestamp.desc()).all()

    def get_transactions_by_portfolio(self, portfolio_id: int):
        return db.session.query(Transaction).filter_by(portfolio_id=portfolio_id).order_by(Transaction.timestamp.desc()).all()

    def get_transactions_by_security(self, security_id: str):
        return db.session.query(Transaction).filter_by(security_id=security_id).order_by(Transaction.timestamp.desc()).all()
