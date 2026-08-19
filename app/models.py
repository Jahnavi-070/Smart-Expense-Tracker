from datetime import datetime, date
from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class User(UserMixin, db.Model):
    """User model for authentication and preferences."""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    currency = db.Column(db.String(10), default='USD', nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    transactions = db.relationship('Transaction', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    budgets = db.relationship('Budget', backref='user', lazy='dynamic', cascade='all, delete-orphan')

    def set_password(self, password):
        """Hashes and stores the user password."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Verifies the hashed user password."""
        return check_password_hash(self.password_hash, password)

    @property
    def currency_symbol(self):
        """Returns the symbol matching user's currency preference."""
        from app.config import Config
        return Config.SUPPORTED_CURRENCIES.get(self.currency, '$')

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'currency': self.currency,
            'currency_symbol': self.currency_symbol,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self):
        return f'<User {self.username}>'


class Transaction(db.Model):
    """Transaction model storing Income and Expense records."""
    __tablename__ = 'transactions'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    type = db.Column(db.String(10), nullable=False)  # 'income' or 'expense'
    amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50), nullable=False, index=True)
    description = db.Column(db.String(200), nullable=False)
    date = db.Column(db.Date, nullable=False, default=date.today, index=True)
    payment_method = db.Column(db.String(50), default='Cash')
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'type': self.type,
            'amount': round(self.amount, 2),
            'category': self.category,
            'description': self.description,
            'date': self.date.strftime('%Y-%m-%d') if self.date else None,
            'payment_method': self.payment_method,
            'notes': self.notes or '',
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self):
        return f'<Transaction {self.type.upper()} {self.amount} - {self.category}>'


class Budget(db.Model):
    """Monthly Budget model for tracking overall or category-level limits."""
    __tablename__ = 'budgets'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    month = db.Column(db.Integer, nullable=False)  # 1 - 12
    year = db.Column(db.Integer, nullable=False)   # e.g., 2026
    amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50), nullable=True)  # None = Overall monthly budget, or category name
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Unique constraint: only one budget per user, year, month, category (category can be None)
    __table_args__ = (
        db.UniqueConstraint('user_id', 'year', 'month', 'category', name='unique_user_budget_per_month_cat'),
    )

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'month': self.month,
            'year': self.year,
            'amount': round(self.amount, 2),
            'category': self.category or 'Overall',
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self):
        cat = self.category or 'Overall'
        return f'<Budget {self.year}-{self.month:02d} [{cat}]: {self.amount}>'
