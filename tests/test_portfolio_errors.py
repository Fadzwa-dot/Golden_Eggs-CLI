import pytest
from app.service.portfolio_service import PortfolioService
from app.service.exceptions import NotFoundError, ValidationError


def test_create_portfolio_for_missing_user(session):
    ps = PortfolioService()
    with pytest.raises(NotFoundError):
        ps.create_portfolio("no-user", "P", "d")


def test_add_investment_insufficient_balance(session, seed_users_and_securities):
    # create a low-balance user
    from app.models.user import User
    from app.db import get_session
    with get_session() as s:
        u = User(username="lowbal", first_name="Low", last_name="Money", password="pw", balance=1.0, role="customer")
        s.add(u)
        s.flush()
    ps = PortfolioService()
    # create portfolio for lowbal
    p = ps.create_portfolio("lowbal", "p", "d")
    with pytest.raises(Exception):
        ps.add_investment("lowbal", p.id, "AAPL", 10, 150.0)


def test_delete_portfolio_with_holdings(session, seed_users_and_securities):
    user = seed_users_and_securities["customer"]
    ps = PortfolioService()
    p = ps.create_portfolio(user.username, "hold", "d")
    # add holding
    ps.add_investment(user.username, p.id, "AAPL", 1, 150.0)
    with pytest.raises(ValidationError):
        ps.delete_portfolio(user.username, p.id)
