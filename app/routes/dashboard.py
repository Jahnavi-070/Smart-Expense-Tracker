from datetime import date
from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user
from app.models import Transaction, Budget
from app.services.insights_service import FinancialInsightsService

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/')
def home():
    """Home landing route redirecting to dashboard or login."""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    return redirect(url_for('auth.login'))


@dashboard_bp.route('/dashboard')
@login_required
def index():
    """Main dashboard page."""
    user_id = current_user.id
    today = date.today()

    # Get calculated financial summaries
    metrics = FinancialInsightsService.get_summary_metrics(user_id, today)

    # Get recent transactions (last 6)
    recent_transactions = Transaction.query.filter_by(user_id=user_id)\
        .order_by(Transaction.date.desc(), Transaction.id.desc())\
        .limit(6).all()

    # Get dynamic smart financial insights
    smart_insights = FinancialInsightsService.generate_smart_insights(user_id)

    # Category breakdown for current month
    category_summary = FinancialInsightsService.get_category_breakdown(user_id, today.month, today.year)

    # Overall and category budgets for current month
    budgets = Budget.query.filter_by(
        user_id=user_id,
        month=today.month,
        year=today.year
    ).all()

    return render_template(
        'dashboard/index.html',
        metrics=metrics,
        recent_transactions=recent_transactions,
        smart_insights=smart_insights,
        category_summary=category_summary,
        budgets=budgets,
        today=today
    )
