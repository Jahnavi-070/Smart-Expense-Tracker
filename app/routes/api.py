from datetime import date
from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from app.services.insights_service import FinancialInsightsService

api_bp = Blueprint('api', __name__, url_prefix='/api')

# Chart color palette matching modern UI theme
CATEGORY_COLORS = {
    'Food': '#f97316',          # Orange
    'Travel': '#3b82f6',        # Blue
    'Shopping': '#ec4899',      # Pink
    'Bills': '#ef4444',         # Red
    'Education': '#8b5cf6',     # Purple
    'Entertainment': '#eab308', # Yellow
    'Health': '#10b981',        # Green
    'Other': '#6b7280',         # Slate Gray
    'Salary': '#22c55e',        # Emerald Green
    'Freelance': '#06b6d4',     # Cyan
    'Investments': '#6366f1',   # Indigo
    'Gift': '#d946ef',          # Fuchsia
    'Allowance': '#14b8a6'      # Teal
}


@api_bp.route('/charts/category-expenses', methods=['GET'])
@login_required
def category_expenses_chart():
    """Returns category breakdown formatted for Chart.js doughnut/pie charts."""
    today = date.today()
    month = request.args.get('month', today.month, type=int)
    year = request.args.get('year', today.year, type=int)

    breakdown = FinancialInsightsService.get_category_breakdown(current_user.id, month, year)
    categories = breakdown['categories']

    labels = [c['category'] for c in categories]
    values = [c['amount'] for c in categories]
    colors = [CATEGORY_COLORS.get(c['category'], '#94a3b8') for c in categories]

    return jsonify({
        'success': True,
        'currency_symbol': current_user.currency_symbol,
        'currency': current_user.currency,
        'total_expenses': breakdown['total_expenses'],
        'labels': labels,
        'values': values,
        'colors': colors,
        'categories_detail': categories
    })


@api_bp.route('/charts/monthly-cashflow', methods=['GET'])
@login_required
def monthly_cashflow_chart():
    """Returns past N months income vs expenses for Chart.js bar/line charts."""
    range_months = request.args.get('range', 6, type=int)
    trend = FinancialInsightsService.get_monthly_cashflow_trend(current_user.id, months_count=range_months)

    labels = [item['month_label'] for item in trend]
    income_data = [item['income'] for item in trend]
    expense_data = [item['expenses'] for item in trend]
    net_data = [item['net'] for item in trend]

    return jsonify({
        'success': True,
        'currency_symbol': current_user.currency_symbol,
        'currency': current_user.currency,
        'labels': labels,
        'income': income_data,
        'expenses': expense_data,
        'net': net_data
    })


@api_bp.route('/charts/daily-spending', methods=['GET'])
@login_required
def daily_spending_chart():
    """Returns day-by-day spending curve for Chart.js line area charts."""
    today = date.today()
    month = request.args.get('month', today.month, type=int)
    year = request.args.get('year', today.year, type=int)

    daily_data = FinancialInsightsService.get_daily_spending_trend(current_user.id, month, year)

    return jsonify({
        'success': True,
        'currency_symbol': current_user.currency_symbol,
        'currency': current_user.currency,
        'labels': daily_data['labels'],
        'daily_values': daily_data['daily_values'],
        'cumulative_values': daily_data['cumulative_values'],
        'month_name': daily_data['month_name']
    })


@api_bp.route('/insights', methods=['GET'])
@login_required
def get_insights():
    """Returns dynamic financial insights."""
    insights = FinancialInsightsService.generate_smart_insights(current_user.id)
    return jsonify({
        'success': True,
        'insights': insights
    })


@api_bp.route('/summary', methods=['GET'])
@login_required
def get_summary():
    """Returns current financial summary metrics."""
    metrics = FinancialInsightsService.get_summary_metrics(current_user.id)
    return jsonify({
        'success': True,
        'metrics': metrics
    })


@api_bp.route('/currency/convert', methods=['GET'])
@login_required
def convert_currency_calc():
    """Live exchange rate conversion calculator API."""
    amount = request.args.get('amount', 1.0, type=float)
    from_curr = request.args.get('from', 'USD').upper()
    to_curr = request.args.get('to', 'INR').upper()

    from app.services.currency_service import CurrencyService
    rate = CurrencyService.get_conversion_rate(from_curr, to_curr)
    converted = round(amount * rate, 2)

    from app.config import Config
    sym_from = Config.SUPPORTED_CURRENCIES.get(from_curr, '')
    sym_to = Config.SUPPORTED_CURRENCIES.get(to_curr, '')

    return jsonify({
        'success': True,
        'amount': amount,
        'from_currency': from_curr,
        'to_currency': to_curr,
        'rate': round(rate, 4),
        'converted_amount': converted,
        'formatted': f"{sym_to}{converted:,.2f}"
    })

