import pytest
from app.service.portfolio_service import PortfolioService
from app.service.security_service import SecurityService
from app.service.user_service import UserService
from app.service.exceptions import NotFoundError, ValidationError


def test_delete_nonexistent_portfolio_raises(session, seed_users_and_securities):
    ps = PortfolioService()
    with pytest.raises(NotFoundError):
        ps.delete_portfolio("alice", 9999)


def test_add_investment_portfolio_not_found(session, seed_users_and_securities):
    ps = PortfolioService()
    with pytest.raises(NotFoundError):
        ps.add_investment("alice", 9999, "AAPL", 1, 150.0)


def test_add_investment_security_not_found(session, seed_users_and_securities):
    ps = PortfolioService()
    p = ps.create_portfolio("alice", "P", "d")
    with pytest.raises(NotFoundError):
        ps.add_investment("alice", p.id, "NOPE", 1, 1.0)


def test_harvest_investment_not_found(session, seed_users_and_securities):
    ps = PortfolioService()
    p = ps.create_portfolio("alice", "P2", "d")
    with pytest.raises(NotFoundError):
        ps.harvest_investment("alice", p.id, "AAPL", 1, 100.0)


def test_user_create_raises_on_session_error(monkeypatch):
    svc = UserService()

    # Monkeypatch the get_session used inside user_service to raise
    import app.service.user_service as user_mod

    def bad_get_session():
        raise RuntimeError("boom")

    # user_service imported get_session at module import time, so patch that
    monkeypatch.setattr(user_mod, "get_session", bad_get_session, raising=False)

    with pytest.raises(ValidationError):
        svc.create_user("F", "L", "u1", "p", 0.0)

def test_login_service_handles_exception(monkeypatch, services):
    # Ensure LoginService.authenticate returns False if the DB layer errors
    from app.service.login_service import LoginService
    import app.service.login_service as lsmod

    def bad_get_session():
        raise RuntimeError("db failure")

    monkeypatch.setattr(lsmod, "get_session", bad_get_session, raising=False)
    login = LoginService()
    assert login.authenticate("admin", "password263") is False
