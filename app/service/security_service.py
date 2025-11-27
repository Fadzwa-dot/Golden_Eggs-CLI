# app/service/security_service.py
from typing import List
from app.db import get_session
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

    def log_transaction(self, session, user_id, portfolio_id, security_id, transaction_type, quantity, price):
        transaction = Transaction(
            user_id=user_id,
            portfolio_id=portfolio_id,
            security_id=security_id,
            transaction_type=transaction_type,
            quantity=quantity,
            price=price
        )
        session.add(transaction)
        session.commit()

    def list_securities(self) -> List[Security]:
        with get_session() as session:
            return session.query(Security).all()

    def get_security(self, ticker: str) -> Security:
        with get_session() as session:
            sec = session.query(Security).filter_by(ticker=ticker).first()
            if not sec:
                raise NotFoundError(f"Ticker '{ticker}' not found")
            return sec

    def buy_security(self, username: str, ticker: str, quantity: int, portfolio_id: int) -> None:
        if quantity <= 0:
            raise ValidationError("Quantity must be positive.")
        with get_session() as session:
            user = session.query(User).filter_by(username=username).first()
            if not user:
                raise NotFoundError(f"User '{username}' not found.")
            if user.role != "customer":
                raise ValidationError("Only customers can buy securities.")
            portfolio = session.query(Portfolio).filter_by(owner_username=username, id=portfolio_id).first()
            if not portfolio:
                raise NotFoundError(f"Portfolio with ID '{portfolio_id}' not found for user '{username}'.")
            security = session.query(Security).filter_by(ticker=ticker).first()
            if not security:
                raise NotFoundError(f"Security '{ticker}' not found in the marketplace.")
            cost = security.price * quantity
            if cost > user.balance:
                raise ValidationError("Insufficient balance to buy security.")
            user.balance -= cost
            existing = session.query(Investment).filter_by(portfolio_id=portfolio_id, security_ticker=ticker).first()
            if existing:
                existing.quantity += quantity
                existing.purchase_price = security.price
            else:
                investment = Investment(portfolio_id=portfolio_id, security_ticker=ticker, quantity=quantity, purchase_price=security.price)
                session.add(investment)
            session.commit()
            # Log transaction
            self.log_transaction(session, username, portfolio_id, ticker, "BUY", quantity, security.price)

    def sell_security(self, username: str, ticker: str, quantity: int, portfolio_id: int) -> None:
        if quantity <= 0:
            raise ValidationError("Quantity must be positive.")
        with get_session() as session:
            user = session.query(User).filter_by(username=username).first()
            if not user:
                raise NotFoundError(f"User '{username}' not found.")
            if user.role != "customer":
                raise ValidationError("Only customers can sell securities.")
            portfolio = session.query(Portfolio).filter_by(owner_username=username, id=portfolio_id).first()
            if not portfolio:
                raise NotFoundError(f"Portfolio with ID '{portfolio_id}' not found for user '{username}'.")
            investment = session.query(Investment).filter_by(portfolio_id=portfolio_id, security_ticker=ticker).first()
            if not investment:
                raise NotFoundError(f"Security '{ticker}' not found in portfolio '{portfolio.name}'.")
            security = session.query(Security).filter_by(ticker=ticker).first()
            if not security:
                raise NotFoundError(f"Security '{ticker}' not found in the marketplace.")
            if quantity > investment.quantity:
                raise ValidationError("Not enough shares to sell.")
            proceeds = quantity * security.price
            investment.quantity -= quantity
            if investment.quantity == 0:
                session.delete(investment)
            user.balance += proceeds
            session.commit()
            # Log transaction
            self.log_transaction(session, username, portfolio_id, ticker, "SELL", quantity, security.price)
    def get_all_transactions(self):
        with get_session() as session:
            return session.query(Transaction).order_by(Transaction.timestamp.desc()).all()

    def get_transactions_by_user(self, username: str):
        with get_session() as session:
            return session.query(Transaction).filter_by(user_id=username).order_by(Transaction.timestamp.desc()).all()

    def get_transactions_by_portfolio(self, portfolio_id: int):
        with get_session() as session:
            return session.query(Transaction).filter_by(portfolio_id=portfolio_id).order_by(Transaction.timestamp.desc()).all()

    def get_transactions_by_security(self, security_id: str):
        with get_session() as session:
            return session.query(Transaction).filter_by(security_id=security_id).order_by(Transaction.timestamp.desc()).all()
