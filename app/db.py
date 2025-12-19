
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
    """Yield a session.

    If the Flask application and `flask_sqlalchemy` extension are initialized,
    return `db.session` so routes use the Flask-managed session. Otherwise,
    fall back to a standalone `SessionLocal` and close it after use.
    """
    # Try to use Flask-SQLAlchemy session if available
    flask_db = None
    try:
        from app.database import db as flask_db  # type: ignore
    except Exception:
        flask_db = None

    if flask_db is not None:
        try:
            yield flask_db.session  # managed by Flask; do not close here
            return
        except Exception:
            # If not within an app context or another error occurs, fall back
            pass

    # Fallback: standalone session
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
