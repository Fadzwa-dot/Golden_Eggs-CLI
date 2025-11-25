# app/service/security_service.py
from typing import List
import db

from app.domain.security import Security
from app.domain.portfolio import Portfolio
from app.service.exceptions import NotFoundError

class SecurityService:
    """
    Simple service to expose securities stored in the top-level `db` module.
    Assumes `db.securities` is a dict mapping ticker -> Security.
    """
    def __init__(self) -> None:
        self.db = db

    def list_securities(self) -> List[Security]:
        """Return all securities available in the marketplace."""
        sec_map = getattr(self.db, "securities", {})
        # ensure we return a list of Security objects (or empty list)
        return list(sec_map.values()) if isinstance(sec_map, dict) else []

    def get_security(self, ticker: str) -> Security:
        """Return a Security by ticker or raise NotFoundError."""
        sec_map = getattr(self.db, "securities", {})
        if not isinstance(sec_map, dict):
            raise NotFoundError(f"Ticker '{ticker}' not found")
        sec = sec_map.get(ticker)
        if sec is None:
            raise NotFoundError(f"Ticker '{ticker}' not found")
        return sec

    def buy_security(self, username: str, ticker: str, quantity: int, portfolio_id: int) -> None:
        """
        Allow a user to buy a security in a specific portfolio.
        Only integer shares allowed.
        """
        if username not in self.db.users:
            raise NotFoundError(f"User '{username}' not found.")

        user = self.db.users[username]
        if user.role != "customer":
            raise PermissionError("Only customers can buy securities.")

        portfolios = self.db.portfolios.get(username, [])
        portfolio = next((p for p in portfolios if p.id == portfolio_id), None)
        if portfolio is None:
            raise NotFoundError(f"Portfolio with ID '{portfolio_id}' not found for user '{username}'.")

        security = self.db.securities.get(ticker)
        if security is None:
            raise NotFoundError(f"Security '{ticker}' not found in the marketplace.")

        total_cost = quantity * security.price
        if total_cost > user.balance:
            raise ValueError("Insufficient balance to buy security.")
        if quantity <= 0:
            raise ValueError("Quantity must be a positive integer.")

        user.adjust_balance(-total_cost)
        portfolio.add_or_update_investment(ticker, quantity, security.price)

    def sell_security(self, username: str, ticker: str, quantity: int, portfolio_id: int) -> None:
        """
        Allow a user to sell a security from a specific portfolio.
        Only integer shares allowed.
        """
        if username not in self.db.users:
            raise NotFoundError(f"User '{username}' not found.")

        user = self.db.users[username]
        if user.role != "customer":
            raise PermissionError("Only customers can sell securities.")

        portfolios = self.db.portfolios.get(username, [])
        portfolio = next((p for p in portfolios if p.id == portfolio_id), None)
        if portfolio is None:
            raise NotFoundError(f"Portfolio with ID '{portfolio_id}' not found for user '{username}'.")

        investment = next((inv for inv in portfolio.holdings if inv.ticker == ticker), None)
        if investment is None:
            raise NotFoundError(f"Security '{ticker}' not found in portfolio '{portfolio.name}'.")

        security = self.db.securities.get(ticker)
        if security is None:
            raise NotFoundError(f"Security '{ticker}' not found in the marketplace.")

        if quantity > investment.quantity:
            raise ValueError("Not enough shares to sell.")
        if quantity <= 0:
            raise ValueError("Quantity must be a positive integer.")

        investment.quantity -= quantity
        if investment.quantity == 0:
            portfolio.holdings.remove(investment)

        proceeds = quantity * security.price
        user.adjust_balance(proceeds)
