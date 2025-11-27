
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker, Session
import os
from contextlib import contextmanager
from typing import Iterator

class Base(DeclarativeBase):
    pass

DATABASE_URL = os.getenv("DATABASE_URL", "mysql+pymysql://root:password@localhost:3306/golden_eggs")
engine = create_engine(
    DATABASE_URL,
    echo=False,
)
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False
)


@contextmanager
def get_session() -> Iterator[Session]:
    """Yield a SQLAlchemy session and ensure it is closed after use.

    Usage:
        with get_session() as session:
            ...
    """
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()

# --- Ensure all tables are created in the database ---
# Import model modules if present; skip if missing to avoid hard failures
try:
    # Individual model modules may or may not exist depending on migrations
    import app.models.user  # type: ignore
except ImportError:
    pass

try:
    import app.models.portfolio  # type: ignore
except ImportError:
    pass

try:
    import app.models.investment  # type: ignore
except ImportError:
    pass

try:
    import app.models.security  # type: ignore
except ImportError:
    pass

try:
    import app.models.transaction  # type: ignore
except ImportError:
    pass

Base.metadata.create_all(engine)
