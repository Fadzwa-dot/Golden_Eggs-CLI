from app.domain.user import User as DomainUser
from app.domain.portfolio import Portfolio as DomainPortfolio
from app.domain.investment import Investment as DomainInvestment
from app.domain.security import Security as DomainSecurity
import pytest


def test_user_full_name_and_balance_and_role():
    u = DomainUser(first_name="Jane", last_name="Doe", username="jdoe", password="pw", balance=10.0, role="customer")
    assert u.full_name() == "Jane Doe"
    u.adjust_balance(5.0)
    assert u.balance == 15.0
    assert not u.is_admin()
    d = u.to_dict()
    assert d["username"] == "jdoe"


def test_investment_value_and_security_to_dict():
    inv = DomainInvestment(ticker="AAPL", quantity=3, purchase_price=100.0)
    assert inv.value() == 300.0
    s = DomainSecurity(ticker="AAPL", issuer="Apple", price=150.0)
    d = s.to_dict()
    assert d["ticker"] == "AAPL"


def test_portfolio_add_update_remove_investment():
    p = DomainPortfolio(id=1, name="P", description="d", holdings=[])
    # add new
    p.add_or_update_investment("aapl", 2, 100.0)
    inv = p.find_investment("AAPL")
    assert inv is not None and inv.quantity == 2
    # update existing
    p.add_or_update_investment("AAPL", 3, 120.0)
    inv = p.find_investment("aapl")
    assert inv.quantity == 5
    # remove partial
    assert p.remove_investment("AAPL", 2) is True
    inv = p.find_investment("AAPL")
    assert inv.quantity == 3
    # remove exact remainder
    assert p.remove_investment("AAPL", 3) is True
    assert p.find_investment("AAPL") is None


def test_portfolio_remove_too_many_raises():
    p = DomainPortfolio(id=2, name="Q", description="desc", holdings=[DomainInvestment(ticker="TSLA", quantity=2, purchase_price=800.0)])
    with pytest.raises(ValueError):
        p.remove_investment("TSLA", 3)
