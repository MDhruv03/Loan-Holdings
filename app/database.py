"""
Database configuration and session management
"""
from sqlmodel import SQLModel, create_engine, Session
from app.config import DATABASE_URL

# Import all models to register them with SQLModel
from app.models.borrower import Borrower, Payment, PrincipalChange
from app.models.holder import Holder, Holding

# Create engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
    pool_pre_ping=True,
    echo=False  # Set to True for debugging
)


def create_db_and_tables():
    """Create database tables"""
    SQLModel.metadata.create_all(engine)


def get_session():
    """Dependency to get database session"""
    with Session(engine) as session:
        yield session
