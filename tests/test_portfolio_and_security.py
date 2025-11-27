from app.db import get_session
from app.models.portfolio import Portfolio
from app.models.investment import Investment
from app.models.transaction import Transaction


def test_create_portfolio_and_add_investment(session, seed_users_and_securities, services):
    customer = seed_users_and_securities["customer"]
    portfolio_service = services["portfolio"]
    security_service = services["security"]

    # create a portfolio
    p = portfolio_service.create_portfolio(customer.username, "My Portfolio", "test portfolio")
    assert isinstance(p, Portfolio)

    # add investment using portfolio service
    inv = portfolio_service.add_investment(customer.username, p.id, "AAPL", 10, 150.0)
    assert isinstance(inv, Investment)
    # verify user balance decreased
    with get_session() as s:
        u = s.query(type(customer)).filter_by(username=customer.username).first()
        assert u.balance < 10000.0


def test_buy_sell_and_transaction_logging(session, seed_users_and_securities, services):
    customer = seed_users_and_securities["customer"]
    security_service = services["security"]

    # create a portfolio first
    from app.service.portfolio_service import PortfolioService
    portfolio_service = PortfolioService()
    p = portfolio_service.create_portfolio(customer.username, "Trading", "for buys")

    # buy
    security_service.buy_security(customer.username, "AAPL", 5, p.id)

    # sell partial
    security_service.sell_security(customer.username, "AAPL", 2, p.id)

    # check transactions logged
    txs = security_service.get_transactions_by_user(customer.username)
    assert len(txs) >= 2
    assert all(isinstance(t, Transaction) for t in txs)


def test_harvest_and_delete_investment(session, seed_users_and_securities, services):
    customer = seed_users_and_securities["customer"]
    portfolio_service = services["portfolio"]

    # create portfolio and add
    p = portfolio_service.create_portfolio(customer.username, "ToSell", "desc")
    holding = portfolio_service.add_investment(customer.username, p.id, "TSLA", 3, 800.0)
    proceeds = portfolio_service.harvest_investment(customer.username, p.id, "TSLA", 3, 800.0)
    assert proceeds == 3 * 800.0
    # verify holding removed
    with get_session() as s:
        inv = s.query(Investment).filter_by(portfolio_id=p.id, security_ticker="TSLA").first()
        assert inv is None
