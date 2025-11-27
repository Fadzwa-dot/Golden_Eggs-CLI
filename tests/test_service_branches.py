import pytest
from app.service.portfolio_service import PortfolioService
from app.service.security_service import SecurityService
from app.service.exceptions import NotFoundError, ValidationError


def test_add_investment_updates_existing_holding(session, seed_users_and_securities):
    customer = seed_users_and_securities["customer"]
    ps = PortfolioService()
    # create a portfolio and add the same security twice
    p = ps.create_portfolio(customer.username, "DoubleUp", "desc")
    inv1 = ps.add_investment(customer.username, p.id, "AAPL", 2, 150.0)
    inv2 = ps.add_investment(customer.username, p.id, "AAPL", 3, 150.0)
    assert inv1.id == inv2.id
    assert inv2.quantity == 5


def test_harvest_negative_quantity_raises(session, seed_users_and_securities):
    customer = seed_users_and_securities["customer"]
    ps = PortfolioService()
    p = ps.create_portfolio(customer.username, "ToHarvest", "desc")
    # add a holding so harvest reaches validation earlier
    ps.add_investment(customer.username, p.id, "TSLA", 2, 800.0)
    with pytest.raises(ValidationError):
        ps.harvest_investment(customer.username, p.id, "TSLA", -1, 800.0)


def test_get_portfolios_by_username_missing_user(session):
    ps = PortfolioService()
    with pytest.raises(NotFoundError):
        ps.get_portfolios_by_username("ghost_user")


def test_get_security_not_found(session):
    ss = SecurityService()
    with pytest.raises(NotFoundError):
        ss.get_security("NO_SUCH")


def test_buy_zero_quantity_raises(session, seed_users_and_securities):
    customer = seed_users_and_securities["customer"]
    ps = PortfolioService()
    ss = SecurityService()
    p = ps.create_portfolio(customer.username, "ZeroBuy", "desc")
    with pytest.raises(ValidationError):
        ss.buy_security(customer.username, "AAPL", 0, p.id)


def test_sell_negative_and_oversell(session, seed_users_and_securities):
    customer = seed_users_and_securities["customer"]
    ps = PortfolioService()
    ss = SecurityService()
    p = ps.create_portfolio(customer.username, "SellTest", "desc")
    # negative quantity
    with pytest.raises(ValidationError):
        ss.sell_security(customer.username, "AAPL", -1, p.id)

    # add a single share and attempt to sell more than owned
    ps.add_investment(customer.username, p.id, "AAPL", 1, 150.0)
    with pytest.raises(ValidationError):
        ss.sell_security(customer.username, "AAPL", 2, p.id)


def test_buy_user_not_found_raises(session, seed_users_and_securities):
    ss = SecurityService()
    # user 'noone' does not exist
    with pytest.raises(NotFoundError):
        ss.buy_security("noone", "AAPL", 1, 1)
