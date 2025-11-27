
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker, Session
import os

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

def get_session() -> Session:
    return SessionLocal()

# --- Ensure all tables are created in the database ---
from app.models.user import User
from app.models.portfolio import Portfolio
from app.models.investment import Investment
from app.models.security import Security
from app.models.transaction import Transaction
Base.metadata.create_all(engine)
