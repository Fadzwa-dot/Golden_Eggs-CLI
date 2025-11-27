import pytest
from app.service.user_service import UserService
from app.service.exceptions import ValidationError, NotFoundError


def test_create_duplicate_username(session, seed_users_and_securities):
    svc = UserService()
    # username 'admin' already seeded
    with pytest.raises(ValidationError):
        svc.create_user("X", "Y", "admin", "pw", 0.0)


def test_delete_nonexistent_user(session):
    svc = UserService()
    with pytest.raises(NotFoundError):
        svc.delete_user("nope")


def test_deposit_invalid_and_nonexistent(session, seed_users_and_securities):
    svc = UserService()
    with pytest.raises(ValueError):
        svc.deposit("admin", -5)
    with pytest.raises(NotFoundError):
        svc.deposit("ghost", 10)


def test_delete_user_with_portfolio(session, seed_users_and_securities):
    from app.service.portfolio_service import PortfolioService
    user = seed_users_and_securities["customer"]
    ps = PortfolioService()
    p = ps.create_portfolio(user.username, "p1", "d")
    svc = UserService()
    with pytest.raises(ValidationError):
        svc.delete_user(user.username)
