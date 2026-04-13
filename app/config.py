"""
Application configuration and settings
"""
import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent


def _normalize_database_url(raw_url: str) -> str:
	"""Normalize DB URLs from platforms like Render/Neon for SQLAlchemy."""
	# Some platforms still provide postgres://; SQLAlchemy expects postgresql://.
	if raw_url.startswith("postgres://"):
		raw_url = raw_url.replace("postgres://", "postgresql://", 1)
	
	if raw_url.startswith("postgresql://"):
		# Since we are using psycopg 3 (psycopg[binary]), we must specify postgresql+psycopg://
		return raw_url.replace("postgresql://", "postgresql+psycopg://", 1)
	return raw_url

# Database
DATABASE_URL = _normalize_database_url(
	os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR}/loans.db")
)

# Security
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
SESSION_COOKIE_NAME = "loan_tracker_session"
SESSION_MAX_AGE = 30 * 24 * 60 * 60  # 30 days

# Application
APP_TITLE = "Loan Tracker"
APP_VERSION = "2.0.0"

# Admin credentials (in production, use environment variables)
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")  # Change this!

# Supported currencies
SUPPORTED_CURRENCIES = ["INR", "THB", "RMB"]
DEFAULT_CURRENCY = "INR"

# Static and template directories
STATIC_DIR = BASE_DIR / "static"
TEMPLATES_DIR = BASE_DIR / "templates"
