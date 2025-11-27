# app/service/portfolio_service.py
from typing import Dict, List, Optional, Any
from app.db import get_session
from app.models.portfolio import Portfolio
from app.models.user import User
from app.models.investment import Investment
from app.models.security import Security
from app.service.exceptions import NotFoundError, ValidationError

class PortfolioService:
    """
    Service to manage portfolios stored in the top-level `db` module.
    Portfolios are Portfolio objects with holdings as list[Investment].
    """

    def __init__(self) -> None:
        pass

    def create_portfolio(self, username: str, name: str, description: str) -> Portfolio:
        with get_session() as session:
            user = session.query(User).filter_by(username=username).first()
            if not user:
                raise NotFoundError(f"user '{username}' not found")
            portfolio = Portfolio(name=name, description=description, owner_username=username)
            session.add(portfolio)
            session.commit()
            return portfolio

    def list_portfolios(self, username: str) -> List[Portfolio]:
        with get_session() as session:
            return session.query(Portfolio).filter_by(owner_username=username).all()

    def get_portfolio(self, username: str, portfolio_id: int) -> Optional[Portfolio]:
        with get_session() as session:
            return session.query(Portfolio).filter_by(owner_username=username, id=portfolio_id).first()

    def delete_portfolio(self, username: str, portfolio_id: int) -> None:
        with get_session() as session:
            portfolio = session.query(Portfolio).filter_by(owner_username=username, id=portfolio_id).first()
            if not portfolio:
                raise NotFoundError(f"portfolio id {portfolio_id} not found for user {username}")
            if portfolio.investments and len(portfolio.investments) > 0:
                raise ValidationError("Portfolio holdings must be empty before deletion.")
            session.delete(portfolio)
            session.commit()

    def add_investment(self, username: str, portfolio_id: int, ticker: str, quantity: int, purchase_price: float) -> Investment:
        if quantity <= 0:
            raise ValidationError("quantity must be positive")
        with get_session() as session:
            portfolio = session.query(Portfolio).filter_by(owner_username=username, id=portfolio_id).first()
            if not portfolio:
                raise NotFoundError("portfolio not found")
            security = session.query(Security).filter_by(ticker=ticker).first()
            if not security:
                raise NotFoundError(f"ticker '{ticker}' not found")
            user = session.query(User).filter_by(username=username).first()
            cost = security.price * quantity
            if user is None or user.balance < cost:
                raise ValidationError("insufficient balance")
            user.balance -= cost
            # find existing holding
            existing = session.query(Investment).filter_by(portfolio_id=portfolio_id, security_ticker=ticker).first()
            if existing:
                existing.quantity += quantity
                existing.purchase_price = purchase_price
                session.commit()
                return existing
            holding = Investment(portfolio_id=portfolio_id, security_ticker=ticker, quantity=quantity, purchase_price=purchase_price)
            session.add(holding)
            session.commit()
            return holding

    def harvest_investment(self, username: str, portfolio_id: int, ticker: str, quantity: int, sale_price: float) -> float:
        if quantity <= 0:
            raise ValidationError("quantity must be positive")
        with get_session() as session:
            portfolio = session.query(Portfolio).filter_by(owner_username=username, id=portfolio_id).first()
            if not portfolio:
                raise NotFoundError("portfolio not found")
            investment = session.query(Investment).filter_by(portfolio_id=portfolio_id, security_ticker=ticker).first()
            if not investment:
                raise NotFoundError(f"investment in '{ticker}' not found")
            held_qty = investment.quantity
            if quantity > held_qty:
                raise ValidationError("not enough shares to harvest")
            user = session.query(User).filter_by(username=username).first()
            proceeds = sale_price * quantity
            investment.quantity -= quantity
            if investment.quantity == 0:
                session.delete(investment)
            user.balance += proceeds
            session.commit()
            return proceeds

    def get_portfolios_by_username(self, username: str) -> List[Portfolio]:
        """
        Retrieve all portfolios for a given username from the database.
        Raises NotFoundError if the user does not exist.
        """
        with get_session() as session:
            user = session.query(User).filter_by(username=username).first()
            if not user:
                raise NotFoundError(f"User '{username}' not found.")
            portfolios = session.query(Portfolio).filter_by(owner_username=username).all()
            return portfolios
