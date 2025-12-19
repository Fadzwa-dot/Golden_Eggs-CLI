# app/service/portfolio_service.py
from typing import Dict, List, Optional, Any
from app.database import db
from sqlalchemy.orm import selectinload
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
        user = db.session.query(User).filter_by(username=username).first()
        if not user:
            raise NotFoundError(f"user '{username}' not found")
        portfolio = Portfolio(name=name, description=description, owner_username=username)
        db.session.add(portfolio)
        db.session.commit()
        _ = portfolio.investments
        return portfolio

    def list_portfolios(self, username: str) -> List[Portfolio]:
        return db.session.query(Portfolio).options(selectinload(Portfolio.investments)).filter_by(owner_username=username).all()

    def list_all_portfolios(self) -> List[Portfolio]:
        """Return all portfolios regardless of owner."""
        return db.session.query(Portfolio).options(selectinload(Portfolio.investments)).all()

    def get_portfolio(self, username: str, portfolio_id: int) -> Optional[Portfolio]:
        return db.session.query(Portfolio).options(selectinload(Portfolio.investments)).filter_by(owner_username=username, id=portfolio_id).first()

    def delete_portfolio(self, username: str, portfolio_id: int) -> None:
        portfolio = db.session.query(Portfolio).filter_by(owner_username=username, id=portfolio_id).first()
        if not portfolio:
            raise NotFoundError(f"portfolio id {portfolio_id} not found for user {username}")
        if portfolio.investments and len(portfolio.investments) > 0:
            raise ValidationError("Portfolio holdings must be empty before deletion.")
        db.session.delete(portfolio)
        db.session.commit()

    def add_investment(self, username: str, portfolio_id: int, ticker: str, quantity: int, purchase_price: float) -> Investment:
        if quantity <= 0:
            raise ValidationError("quantity must be positive")
        portfolio = db.session.query(Portfolio).filter_by(owner_username=username, id=portfolio_id).first()
        if not portfolio:
            raise NotFoundError("portfolio not found")
        security = db.session.query(Security).filter_by(ticker=ticker).first()
        if not security:
            raise NotFoundError(f"ticker '{ticker}' not found")
        user = db.session.query(User).filter_by(username=username).first()
        cost = security.price * quantity
        if user is None or user.balance < cost:
            raise ValidationError("insufficient balance")
        user.balance -= cost
        existing = db.session.query(Investment).filter_by(portfolio_id=portfolio_id, security_ticker=ticker).first()
        if existing:
            existing.quantity += quantity
            existing.purchase_price = purchase_price
            db.session.commit()
            return existing
        holding = Investment(portfolio_id=portfolio_id, security_ticker=ticker, quantity=quantity, purchase_price=purchase_price)
        db.session.add(holding)
        db.session.commit()
        return holding

    def harvest_investment(self, username: str, portfolio_id: int, ticker: str, quantity: int, sale_price: float) -> float:
        if quantity <= 0:
            raise ValidationError("quantity must be positive")
        portfolio = db.session.query(Portfolio).filter_by(owner_username=username, id=portfolio_id).first()
        if not portfolio:
            raise NotFoundError("portfolio not found")
        investment = db.session.query(Investment).filter_by(portfolio_id=portfolio_id, security_ticker=ticker).first()
        if not investment:
            raise NotFoundError(f"investment in '{ticker}' not found")
        held_qty = investment.quantity
        if quantity > held_qty:
            raise ValidationError("not enough shares to harvest")
        user = db.session.query(User).filter_by(username=username).first()
        proceeds = sale_price * quantity
        investment.quantity -= quantity
        if investment.quantity == 0:
            db.session.delete(investment)
        user.balance += proceeds
        db.session.commit()
        return proceeds

    def get_portfolios_by_username(self, username: str) -> List[Portfolio]:
        """
        Retrieve all portfolios for a given username from the database.
        Raises NotFoundError if the user does not exist.
        """
        user = db.session.query(User).filter_by(username=username).first()
        if not user:
            raise NotFoundError(f"User '{username}' not found.")
        portfolios = db.session.query(Portfolio).options(selectinload(Portfolio.investments)).filter_by(owner_username=username).all()
        return portfolios
