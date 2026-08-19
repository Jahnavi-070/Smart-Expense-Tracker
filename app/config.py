import os
from datetime import timedelta

BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))


class Config:
    """Base application configuration."""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'smart-expense-tracker-dev-key-2026-secure')
    
    # SQLite Database URI in instance folder
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        f"sqlite:///{os.path.join(BASE_DIR, 'instance', 'expense_tracker.db')}"
    )
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
