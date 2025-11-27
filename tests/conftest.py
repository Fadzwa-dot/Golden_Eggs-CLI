import os
import sys
import importlib
import pytest

# Make sure the project root is on sys.path so `import app` works when pytest runs
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

# Ensure tests use in-memory SQLite
os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")

# If app.db already imported, reload it after setting DATABASE_URL
if "app.db" in sys.modules:
    importlib.reload(sys.modules["app.db"])
else:
    importlib.import_module("app.db")

from app import db as app_db
from app.db import get_session
from sqlalchemy.orm import sessionmaker
from app.models.user import User
from app.models.security import Security
from app.models.portfolio import Portfolio

# Create tables explicitly to ensure models are registered
app_db.Base.metadata.create_all(app_db.engine)

@pytest.fixture(scope="session")
def engine():
    return app_db.engine

@pytest.fixture(scope="function")
def session():
    """Provide a transactional scope around a test using a single connection.

    We bind `app.db.SessionLocal` to a sessionmaker bound to a single
    connection so that any commits performed by application code during
    the test occur on the same DB connection and can be rolled back by
    the fixture teardown.
    """
    # Open a connection and begin a transaction
    connection = app_db.engine.connect()
    transaction = connection.begin()

    # Bind a sessionmaker to the connection and replace app.db.SessionLocal
    testing_session_factory = sessionmaker(bind=connection, autoflush=False, autocommit=False, expire_on_commit=False)
    original_session_local = getattr(app_db, "SessionLocal", None)
    app_db.SessionLocal = testing_session_factory

    # Provide a session for the test
    sess = testing_session_factory()
    try:
        yield sess
    finally:
        sess.close()
        # rollback the outer transaction and restore original SessionLocal
        try:
            transaction.rollback()
        finally:
            connection.close()
            if original_session_local is not None:
                app_db.SessionLocal = original_session_local

@pytest.fixture(scope="function")
def seed_users_and_securities(session):
    # create an admin and a customer and some securities
    admin = User(username="admin", first_name="Admin", last_name="User", password="password263", balance=0.0, role="admin")
    customer = User(username="alice", first_name="Alice", last_name="Buyer", password="alicepwd", balance=10000.0, role="customer")
    # Add objects and flush instead of commit so the outer transactional fixture can rollback
    session.add_all([admin, customer])
    session.flush()

    sec1 = Security(ticker="AAPL", name="Apple Inc", price=150.0)
    sec2 = Security(ticker="TSLA", name="Tesla Inc", price=800.0)
    session.add_all([sec1, sec2])
    session.flush()
    return {"admin": admin, "customer": customer, "securities": [sec1, sec2]}

@pytest.fixture(scope="function")
def services():
    # import services lazily
    from app.service.login_service import LoginService
    from app.service.user_service import UserService
    from app.service.portfolio_service import PortfolioService
    from app.service.security_service import SecurityService

    return {
        "login": LoginService(),
        "user": UserService(),
        "portfolio": PortfolioService(),
        "security": SecurityService(),
    }
