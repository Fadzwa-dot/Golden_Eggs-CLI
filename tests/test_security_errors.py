import pytest
from app.service.security_service import SecurityService
from app.service.exceptions import ValidationError, NotFoundError


def test_buy_negative_quantity(session, seed_users_and_securities):
    ss = SecurityService()
    with pytest.raises(ValidationError):
        ss.buy_security("alice", "AAPL", -1, 1)


def test_buy_as_admin(session, seed_users_and_securities):
    ss = SecurityService()
    # admin user exists in seed
    with pytest.raises(ValidationError):
        ss.buy_security("admin", "AAPL", 1, 1)


def test_sell_not_in_portfolio(session, seed_users_and_securities):
    ss = SecurityService()
    # ensure portfolio exists for alice
    from app.service.portfolio_service import PortfolioService
    ps = PortfolioService()
    p = ps.create_portfolio("alice", "tr", "d")
    with pytest.raises(NotFoundError):
        ss.sell_security("alice", "TSLA", 1, p.id)
