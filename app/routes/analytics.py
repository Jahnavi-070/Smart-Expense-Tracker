import os
import sys
from datetime import date
from flask import Blueprint, render_template, request
from flask_login import login_required, current_user
from sqlalchemy import func

# Ensure project root is in sys.path if run directly
_PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from app.models import db, Transaction
from app.services.insights_service import FinancialInsightsService

analytics_bp = Blueprint('analytics', __name__, url_prefix='/analytics')


@analytics_bp.route('', methods=['GET'])
@login_required
def index():
    """Analytics view with comprehensive charts, trends, and financial breakdown."""
    today = date.today()
    month = request.args.get('month', today.month, type=int)
    year = request.args.get('year', today.year, type=int)
    range_months = request.args.get('range', 6, type=int)

    user_id = current_user.id

    # 1. Summary metrics
    metrics = FinancialInsightsService.get_summary_metrics(user_id, date(year, month, 1))

    # 2. Category Breakdown
    cat_breakdown = FinancialInsightsService.get_category_breakdown(user_id, month, year)

    # 3. Monthly Cashflow Trend (Past N months)
    cashflow_trend = FinancialInsightsService.get_monthly_cashflow_trend(user_id, months_count=range_months)

    # 4. Daily Spending Velocity
    daily_trend = FinancialInsightsService.get_daily_spending_trend(user_id, month, year)

    # 5. Calculate analytics averages
    total_months_active = max(1, len(cashflow_trend))
    total_period_spent = sum(item['expenses'] for item in cashflow_trend)
    total_period_income = sum(item['income'] for item in cashflow_trend)

    avg_monthly_expense = total_period_spent / total_months_active
    avg_monthly_income = total_period_income / total_months_active
    period_savings_rate = ((total_period_income - total_period_spent) / total_period_income * 100) if total_period_income > 0 else 0.0

    # Top spending category all-time
    top_cat_all_time = db.session.query(
        Transaction.category,
        func.sum(Transaction.amount).label('total')
    ).filter(
        Transaction.user_id == user_id,
        Transaction.type == 'expense'
    ).group_by(Transaction.category).order_by(func.sum(Transaction.amount).desc()).first()

    return render_template(
        'analytics/index.html',
        metrics=metrics,
        cat_breakdown=cat_breakdown,
        cashflow_trend=cashflow_trend,
        daily_trend=daily_trend,
        avg_monthly_expense=round(avg_monthly_expense, 2),
        avg_monthly_income=round(avg_monthly_income, 2),
        period_savings_rate=round(period_savings_rate, 1),
        top_cat_all_time=top_cat_all_time,
        month=month,
        year=year,
        range_months=range_months,
        month_name=date(year, month, 1).strftime('%B %Y')
    )
