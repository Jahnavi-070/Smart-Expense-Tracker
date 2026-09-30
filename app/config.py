import os
from datetime import timedelta

BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))


# On Vercel / AWS Lambda serverless environments, only /tmp is writable
if os.environ.get('VERCEL'):
    DEFAULT_DB_DIR = "/tmp/instance"
    DEFAULT_DB_PATH = os.path.join(DEFAULT_DB_DIR, "expense_tracker.db")
else:
    DEFAULT_DB_DIR = os.path.join(BASE_DIR, "instance")
    DEFAULT_DB_PATH = os.path.join(DEFAULT_DB_DIR, "expense_tracker.db")


class Config:
    """Base application configuration."""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'smart-expense-tracker-dev-key-2026-secure')
    
    # SQLite Database URI (or PostgreSQL if DATABASE_URL provided)
    _raw_db_url = os.environ.get('DATABASE_URL')
    if _raw_db_url and _raw_db_url.startswith('postgres://'):
        _raw_db_url = _raw_db_url.replace('postgres://', 'postgresql://', 1)
    
    SQLALCHEMY_DATABASE_URI = _raw_db_url or f"sqlite:///{DEFAULT_DB_PATH}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Session Configuration
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Currency symbols supported
    SUPPORTED_CURRENCIES = {
        'USD': '$',
        'EUR': '€',
        'GBP': '£',
        'INR': '₹',
        'CAD': 'CA$',
        'AUD': 'A$',
        'JPY': '¥',
        'AED': 'AED ',
        'SGD': 'S$',
        'CHF': 'CHF ',
        'BRL': 'R$',
        'CNY': '¥',
        'KRW': '₩',
        'MXN': 'Mex$'
    }
    
    # Expense and Income category presets
    EXPENSE_CATEGORIES = [
        'Food',
        'Travel',
        'Shopping',
        'Bills',
        'Education',
        'Entertainment',
        'Health',
        'Other'
    ]
    
    INCOME_CATEGORIES = [
        'Salary',
        'Freelance',
        'Investments',
        'Gift',
        'Allowance',
        'Other'
    ]
    
    PAYMENT_METHODS = [
        'Cash',
        'Credit Card',
        'Debit Card',
        'UPI / Online',
        'Bank Transfer',
        'Other'
    ]


class TestConfig(Config):
    """Testing configuration."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
    SECRET_KEY = 'test-secret-key'
