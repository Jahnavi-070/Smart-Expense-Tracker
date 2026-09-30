import os
import sys
import re
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user

# Ensure project root is in sys.path if run directly
_PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from app.models import db, User

auth_bp = Blueprint('auth', __name__)


def is_valid_email(email):
    """Helper to validate email format."""
    pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(pattern, email) is not None


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """User registration route."""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        currency = request.form.get('currency', 'USD').strip().upper()

        errors = []

        # Validations
        if not username or len(username) < 3 or len(username) > 30:
            errors.append('Username must be between 3 and 30 characters.')
        elif not re.match(r'^[a-zA-Z0-9_]+$', username):
            errors.append('Username can only contain letters, numbers, and underscores.')

        if not email or not is_valid_email(email):
            errors.append('Please provide a valid email address.')

        if not password or len(password) < 6:
            errors.append('Password must be at least 6 characters long.')

        if password != confirm_password:
            errors.append('Passwords do not match.')

        # Check existing user
        if not errors:
            if User.query.filter_by(username=username).first():
                errors.append('Username is already taken. Please choose another.')
            elif User.query.filter_by(email=email).first():
                errors.append('Email is already registered. Please log in.')

        if errors:
            for error in errors:
                flash(error, 'danger')
            return render_template(
                'auth/register.html',
                username=username,
                email=email,
                currency=currency
            )

        # Create user
        new_user = User(username=username, email=email, currency=currency)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        login_user(new_user)
        flash('Account created successfully! Welcome to Smart Expense Tracker.', 'success')
        return redirect(url_for('dashboard.index'))

    return render_template('auth/register.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login route."""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))

    if request.method == 'POST':
        identifier = request.form.get('identifier', '').strip()
        password = request.form.get('password', '')
        remember = bool(request.form.get('remember'))

        if not identifier or not password:
            flash('Please fill in all fields.', 'danger')
            return render_template('auth/login.html', identifier=identifier)

        # Allow login via username or email
        user = User.query.filter(
            (User.username == identifier) | (User.email == identifier.lower())
        ).first()

        if user and user.check_password(password):
            login_user(user, remember=remember)
            flash(f'Welcome back, {user.username}!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('dashboard.index'))
        else:
            flash('Invalid username/email or password. Please try again.', 'danger')
            return render_template('auth/login.html', identifier=identifier)

    return render_template('auth/login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    """User logout route."""
    logout_user()
    flash('You have been safely logged out.', 'info')
    return redirect(url_for('auth.login'))


@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """User profile and preferences management."""
    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'update_profile':
            username = request.form.get('username', '').strip()
            email = request.form.get('email', '').strip().lower()
            currency = request.form.get('currency', 'USD').strip().upper()
            convert_amounts = bool(request.form.get('convert_amounts'))

            errors = []
            if not username or len(username) < 3:
                errors.append('Username must be at least 3 characters.')
            if not email or not is_valid_email(email):
                errors.append('Valid email is required.')

            # Check if updated username/email conflicts with another user
            existing_user = User.query.filter(User.username == username, User.id != current_user.id).first()
            if existing_user:
                errors.append('Username is already taken.')

            existing_email = User.query.filter(User.email == email, User.id != current_user.id).first()
            if existing_email:
                errors.append('Email is already in use by another account.')

            if errors:
                for err in errors:
                    flash(err, 'danger')
            else:
                from app.services.currency_service import CurrencyService
                old_curr = current_user.currency
                current_user.username = username
                current_user.email = email

                if currency != old_curr:
                    if convert_amounts:
                        t_count, b_count, rate = CurrencyService.convert_user_data(current_user, currency)
                        db.session.commit()
                        flash(f"Updated preferences and converted {t_count} transactions & {b_count} budgets from {old_curr} to {currency} (Rate: 1 {old_curr} = {rate:.4f} {currency}).", 'success')
                    else:
                        current_user.currency = currency
                        db.session.commit()
                        flash(f"Profile preferences updated. Currency set to {currency} ({current_user.currency_symbol}).", 'success')
                else:
                    db.session.commit()
                    flash('Profile preferences updated successfully!', 'success')

        elif action == 'change_password':
            old_password = request.form.get('old_password', '')
            new_password = request.form.get('new_password', '')
            confirm_password = request.form.get('confirm_password', '')

            if not current_user.check_password(old_password):
                flash('Current password is incorrect.', 'danger')
            elif len(new_password) < 6:
                flash('New password must be at least 6 characters.', 'danger')
            elif new_password != confirm_password:
                flash('New passwords do not match.', 'danger')
            else:
                current_user.set_password(new_password)
                db.session.commit()
                flash('Password changed successfully!', 'success')

        return redirect(url_for('auth.profile'))

    from app.services.currency_service import CurrencyService
    return render_template(
        'auth/profile.html',
        exchange_rates=CurrencyService.EXCHANGE_RATES_TO_USD
    )


@auth_bp.route('/set-currency', methods=['POST'])
@login_required
def set_currency():
    """Quick currency switcher that converts all transaction and budget amounts automatically."""
    currency = request.form.get('currency', 'USD').strip().upper()
    # Default to True unless convert='0'
    convert_param = request.form.get('convert')
    convert_amounts = (convert_param != '0')
    
    from app.config import Config
    from app.services.currency_service import CurrencyService

    if currency in Config.SUPPORTED_CURRENCIES:
        old_currency = current_user.currency
        if old_currency != currency:
            if convert_amounts:
                t_count, b_count, rate = CurrencyService.convert_user_data(current_user, currency)
                db.session.commit()
                flash(f"Converted all {t_count} transactions & budgets from {old_currency} to {currency} ({current_user.currency_symbol}) at rate 1 {old_currency} = {rate:.2f} {currency}!", 'success')
            else:
                current_user.currency = currency
                db.session.commit()
                flash(f"Currency symbol switched to {currency} ({current_user.currency_symbol}).", 'info')

    return redirect(request.referrer or url_for('dashboard.index'))



