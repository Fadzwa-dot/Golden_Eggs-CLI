from app.db import get_session
from app.models.transaction import Transaction


def test_user_list_and_get_portfolio(session, seed_users_and_securities, services):
    user_svc = services["user"]
    ps = services["portfolio"]
    users = user_svc.list_users()
    usernames = {u.username for u in users}
    assert "admin" in usernames and "alice" in usernames

    # get_portfolio returns None for missing
    p = ps.get_portfolio("alice", 99999)
    assert p is None

    # create and then fetch
    created = ps.create_portfolio("alice", "FetchMe", "x")
    fetched = ps.get_portfolio("alice", created.id)
    assert fetched is not None and fetched.id == created.id


def test_delete_portfolio_success(session, seed_users_and_securities, services):
    ps = services["portfolio"]
    # create a portfolio and ensure it's deletable (no holdings)
    p = ps.create_portfolio("alice", "ToDelete", "d")
    # should delete without errors
    ps.delete_portfolio("alice", p.id)
    # ensure gone from DB
    with get_session() as s:
        from app.models.portfolio import Portfolio

        assert s.query(Portfolio).filter_by(id=p.id).first() is None


def test_transaction_query_methods(session, seed_users_and_securities, services):
    sec_svc = services["security"]
    ps = services["portfolio"]
    customer = seed_users_and_securities["customer"]

    # create a portfolio and perform buys/sells
    p = ps.create_portfolio(customer.username, "Txs", "d")
    sec_svc.buy_security(customer.username, "AAPL", 2, p.id)
    sec_svc.sell_security(customer.username, "AAPL", 1, p.id)

    all_txs = sec_svc.get_all_transactions()
    assert len(all_txs) >= 2

    by_user = sec_svc.get_transactions_by_user(customer.username)
    assert all(t.user_id == customer.username for t in by_user)

    by_port = sec_svc.get_transactions_by_portfolio(p.id)
    assert all(t.portfolio_id == p.id for t in by_port)

    by_sec = sec_svc.get_transactions_by_security("AAPL")
    assert all(t.security_id == "AAPL" for t in by_sec)
