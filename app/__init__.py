import os
from datetime import datetime
from flask import Flask, render_template
from flask_login import LoginManager
from app.config import Config
from app.models import db, User

login_manager = LoginManager()


def create_app(config_class=Config):
    """Application factory for Smart Expense Tracker."""
    instance_path = "/tmp/instance" if os.environ.get("VERCEL") else os.path.join(os.path.dirname(os.path.dirname(__file__)), "instance")
    app = Flask(__name__, instance_relative_config=True, instance_path=instance_path)
    app.config.from_object(config_class)

    # Ensure the instance directory exists for SQLite
    os.makedirs(app.instance_path, exist_ok=True)

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)

    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.dashboard import dashboard_bp
    from app.routes.transactions import transactions_bp
    from app.routes.budgets import budgets_bp
    from app.routes.analytics import analytics_bp
    from app.routes.api import api_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(transactions_bp)
    app.register_blueprint(budgets_bp)
    app.register_blueprint(analytics_bp)
    app.register_blueprint(api_bp)

    # Global context processors for templates
    @app.context_processor
    def inject_global_vars():
        return {
            'now': datetime.utcnow(),
            'expense_categories': Config.EXPENSE_CATEGORIES,
            'income_categories': Config.INCOME_CATEGORIES,
            'payment_methods': Config.PAYMENT_METHODS,
            'supported_currencies': Config.SUPPORTED_CURRENCIES
        }

    # Error handlers
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('errors/500.html'), 500

    # Auto-create tables in development
    with app.app_context():
        db.create_all()

    return app
