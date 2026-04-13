"""
Database configuration and session management
"""
from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy import inspect, text
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


def _ensure_legacy_schema_compatibility():
    """Add missing columns for existing databases created before newer releases."""
    with engine.begin() as connection:
        inspector = inspect(connection)
        table_names = set(inspector.get_table_names())
        if "borrower" not in table_names:
            return

        borrower_columns = {col["name"] for col in inspector.get_columns("borrower")}
        statements = []

        if "is_defaulted" not in borrower_columns:
            # SQLite uses 0/1 for booleans normally via ALTER TABLE, but Postgres strictly requires FALSE
            statements.append("ALTER TABLE borrower ADD COLUMN is_defaulted BOOLEAN DEFAULT FALSE")
        if "defaulted_on" not in borrower_columns:
            statements.append("ALTER TABLE borrower ADD COLUMN defaulted_on DATE")
        if "default_note" not in borrower_columns:
            statements.append("ALTER TABLE borrower ADD COLUMN default_note VARCHAR")

        for statement in statements:
            connection.execute(text(statement))


def create_db_and_tables():
    """Create database tables"""
    SQLModel.metadata.create_all(engine)
    _ensure_legacy_schema_compatibility()


def get_session():
    """Dependency to get database session"""
    with Session(engine) as session:
        yield session
