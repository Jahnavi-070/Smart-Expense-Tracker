from datetime import date, datetime, timedelta
from calendar import monthrange
from sqlalchemy import func, extract
from app.models import db, Transaction, Budget


class FinancialInsightsService:
    """Service to compute metrics, chart datasets, and rule-based smart insights."""

    @staticmethod
    def get_summary_metrics(user_id, target_date=None):
        """Calculates total income, expenses, balance, and current month metrics."""
        if target_date is None:
            target_date = date.today()

        current_month = target_date.month
        current_year = target_date.year

        # All-time Income & Expenses
        all_income = db.session.query(func.coalesce(func.sum(Transaction.amount), 0.0))\
            .filter(Transaction.user_id == user_id, Transaction.type == 'income').scalar()

        all_expenses = db.session.query(func.coalesce(func.sum(Transaction.amount), 0.0))\
            .filter(Transaction.user_id == user_id, Transaction.type == 'expense').scalar()

        current_balance = all_income - all_expenses

        # Current Month Income & Expenses
        month_income = db.session.query(func.coalesce(func.sum(Transaction.amount), 0.0))\
            .filter(
                Transaction.user_id == user_id,
                Transaction.type == 'income',
                extract('month', Transaction.date) == current_month,
                extract('year', Transaction.date) == current_year
            ).scalar()

        month_expenses = db.session.query(func.coalesce(func.sum(Transaction.amount), 0.0))\
            .filter(
                Transaction.user_id == user_id,
                Transaction.type == 'expense',
                extract('month', Transaction.date) == current_month,
                extract('year', Transaction.date) == current_year
            ).scalar()

        month_savings = month_income - month_expenses
        savings_rate = (month_savings / month_income * 100) if month_income > 0 else 0.0

        # Overall Budget for current month
        overall_budget = Budget.query.filter_by(
            user_id=user_id,
            month=current_month,
            year=current_year,
            category=None
        ).first()

        budget_amount = overall_budget.amount if overall_budget else 0.0
        budget_remaining = budget_amount - month_expenses if budget_amount > 0 else 0.0
        budget_percent = (month_expenses / budget_amount * 100) if budget_amount > 0 else 0.0

        # Total transaction count
        transaction_count = Transaction.query.filter_by(user_id=user_id).count()

        return {
            'all_time_income': round(all_income, 2),
            'all_time_expenses': round(all_expenses, 2),
            'current_balance': round(current_balance, 2),
            'month_income': round(month_income, 2),
            'month_expenses': round(month_expenses, 2),
            'month_savings': round(month_savings, 2),
            'savings_rate': round(savings_rate, 1),
            'budget_amount': round(budget_amount, 2),
            'budget_remaining': round(budget_remaining, 2),
            'budget_percent': round(budget_percent, 1),
            'transaction_count': transaction_count,
            'current_month_name': target_date.strftime('%B %Y')
        }

    @staticmethod
    def get_category_breakdown(user_id, month=None, year=None):
        """Returns expense total and percentage per category."""
        target_date = date.today()
        month = month or target_date.month
        year = year or target_date.year

        category_data = db.session.query(
            Transaction.category,
            func.sum(Transaction.amount).label('total')
        ).filter(
            Transaction.user_id == user_id,
            Transaction.type == 'expense',
            extract('month', Transaction.date) == month,
            extract('year', Transaction.date) == year
        ).group_by(Transaction.category).order_by(func.sum(Transaction.amount).desc()).all()

        total_expenses = sum(item.total for item in category_data) if category_data else 0.0

        results = []
        for cat, amount in category_data:
            pct = (amount / total_expenses * 100) if total_expenses > 0 else 0
            results.append({
                'category': cat,
                'amount': round(amount, 2),
                'percentage': round(pct, 1)
            })

        return {
            'total_expenses': round(total_expenses, 2),
            'categories': results
        }

    @staticmethod
    def get_monthly_cashflow_trend(user_id, months_count=6):
        """Returns monthly income vs expenses for the past N months."""
        today = date.today()
        monthly_data = []

        for i in range(months_count - 1, -1, -1):
            # Calculate year and month
            calc_year = today.year
            calc_month = today.month - i
            while calc_month <= 0:
                calc_month += 12
                calc_year -= 1

            month_label = date(calc_year, calc_month, 1).strftime('%b %Y')

            income = db.session.query(func.coalesce(func.sum(Transaction.amount), 0.0))\
                .filter(
                    Transaction.user_id == user_id,
                    Transaction.type == 'income',
                    extract('month', Transaction.date) == calc_month,
                    extract('year', Transaction.date) == calc_year
                ).scalar()

            expenses = db.session.query(func.coalesce(func.sum(Transaction.amount), 0.0))\
                .filter(
                    Transaction.user_id == user_id,
                    Transaction.type == 'expense',
                    extract('month', Transaction.date) == calc_month,
                    extract('year', Transaction.date) == calc_year
                ).scalar()

            monthly_data.append({
                'month_label': month_label,
                'year': calc_year,
                'month': calc_month,
                'income': round(income, 2),
                'expenses': round(expenses, 2),
                'net': round(income - expenses, 2)
            })

        return monthly_data

    @staticmethod
    def get_daily_spending_trend(user_id, month=None, year=None):
        """Returns day-by-day spending for the specified month."""
        today = date.today()
        month = month or today.month
        year = year or today.year

        num_days = monthrange(year, month)[1]
        
        # Query daily spending
        daily_records = db.session.query(
            extract('day', Transaction.date).label('day'),
            func.sum(Transaction.amount).label('total')
        ).filter(
            Transaction.user_id == user_id,
            Transaction.type == 'expense',
            extract('month', Transaction.date) == month,
            extract('year', Transaction.date) == year
        ).group_by(extract('day', Transaction.date)).all()

        daily_dict = {int(r.day): float(r.total) for r in daily_records}

        labels = []
        values = []
        cumulative_values = []
        running_total = 0.0

        for day in range(1, num_days + 1):
            val = daily_dict.get(day, 0.0)
            running_total += val
            labels.append(f"{day}")
            values.append(round(val, 2))
            cumulative_values.append(round(running_total, 2))

        return {
            'labels': labels,
            'daily_values': values,
            'cumulative_values': cumulative_values,
            'month_name': date(year, month, 1).strftime('%B %Y')
        }

    @staticmethod
    def generate_smart_insights(user_id):
        """Generates dynamic, rule-based actionable insights for the user."""
        today = date.today()
        current_month = today.month
        current_year = today.year

        from app.models import User
        user = User.query.get(user_id)
        sym = user.currency_symbol if user else '$'

        insights = []

        # Previous month
        prev_month = current_month - 1 if current_month > 1 else 12
        prev_year = current_year if current_month > 1 else current_year - 1

        # 1. Current vs Previous Month Spending (MoM)
        curr_spent = db.session.query(func.coalesce(func.sum(Transaction.amount), 0.0))\
            .filter(
                Transaction.user_id == user_id,
                Transaction.type == 'expense',
                extract('month', Transaction.date) == current_month,
                extract('year', Transaction.date) == current_year
            ).scalar()

        prev_spent = db.session.query(func.coalesce(func.sum(Transaction.amount), 0.0))\
            .filter(
                Transaction.user_id == user_id,
                Transaction.type == 'expense',
                extract('month', Transaction.date) == prev_month,
                extract('year', Transaction.date) == prev_year
            ).scalar()

        if prev_spent > 0 and curr_spent > 0:
            diff = curr_spent - prev_spent
            pct_change = abs((diff / prev_spent) * 100)
            if diff < 0:
                insights.append({
                    'type': 'success',
                    'icon': 'trending-down',
                    'title': 'Spending Reduction',
                    'message': f"Great job! You spent {pct_change:.1f}% less this month ({sym}{curr_spent:,.2f}) compared to last month ({sym}{prev_spent:,.2f})."
                })
            elif diff > 0:
                insights.append({
                    'type': 'warning',
                    'icon': 'trending-up',
                    'title': 'Higher Spending Velocity',
                    'message': f"Your spending this month ({sym}{curr_spent:,.2f}) is {pct_change:.1f}% higher than last month ({sym}{prev_spent:,.2f}). Monitor upcoming expenses."
                })

        # 2. Top Category Dominance
        cat_breakdown = FinancialInsightsService.get_category_breakdown(user_id, current_month, current_year)
        if cat_breakdown['categories']:
            top_cat = cat_breakdown['categories'][0]
            if top_cat['percentage'] >= 30:
                insights.append({
                    'type': 'info',
                    'icon': 'pie-chart',
                    'title': f"High {top_cat['category']} Allocation",
                    'message': f"{top_cat['category']} accounts for {top_cat['percentage']:.1f}% of your monthly expenses ({sym}{top_cat['amount']:,.2f}). Consider allocating a specific category budget."
                })

        # 3. Monthly Budget Health Check
        budget = Budget.query.filter_by(
            user_id=user_id,
            month=current_month,
            year=current_year,
            category=None
        ).first()

        days_in_month = monthrange(current_year, current_month)[1]
        days_remaining = max(1, days_in_month - today.day)

        if budget and budget.amount > 0:
            spent_pct = (curr_spent / budget.amount) * 100
            remaining = budget.amount - curr_spent

            if spent_pct > 100:
                insights.append({
                    'type': 'danger',
                    'icon': 'alert-triangle',
                    'title': 'Budget Exceeded',
                    'message': f"You have exceeded your monthly budget of {sym}{budget.amount:,.2f} by {sym}{abs(remaining):,.2f} ({spent_pct:.1f}% utilized)."
                })
            elif spent_pct >= 85:
                daily_allowance = max(0.0, remaining / days_remaining)
                insights.append({
                    'type': 'warning',
                    'icon': 'alert-circle',
                    'title': 'Budget Alert (Over 85%)',
                    'message': f"You've used {spent_pct:.1f}% of your budget. You have {sym}{remaining:,.2f} left for {days_remaining} days (~{sym}{daily_allowance:.2f}/day)."
                })
            else:
                daily_allowance = remaining / days_remaining
                insights.append({
                    'type': 'success',
                    'icon': 'shield-check',
                    'title': 'Budget On Track',
                    'message': f"You are well within your {sym}{budget.amount:,.2f} budget ({spent_pct:.1f}% used). Spend limit: ~{sym}{daily_allowance:.2f}/day for the remaining {days_remaining} days."
                })
        elif curr_spent > 0:
            insights.append({
                'type': 'info',
                'icon': 'target',
                'title': 'Set a Monthly Budget',
                'message': f"You have recorded {sym}{curr_spent:,.2f} in expenses this month. Set a monthly budget to get real-time tracking and pacing alerts!"
            })

        # 4. Savings Rate Insight
        curr_income = db.session.query(func.coalesce(func.sum(Transaction.amount), 0.0))\
            .filter(
                Transaction.user_id == user_id,
                Transaction.type == 'income',
                extract('month', Transaction.date) == current_month,
                extract('year', Transaction.date) == current_year
            ).scalar()

        if curr_income > 0:
            savings = curr_income - curr_spent
            savings_pct = (savings / curr_income) * 100
            if savings_pct >= 20:
                insights.append({
                    'type': 'success',
                    'icon': 'award',
                    'title': 'Healthy Savings Rate',
                    'message': f"Your savings rate this month is {savings_pct:.1f}% ({sym}{savings:,.2f} saved). Financial advisors recommend aiming for at least 20%."
                })
            elif savings_pct > 0:
                insights.append({
                    'type': 'warning',
                    'icon': 'compass',
                    'title': 'Modest Savings',
                    'message': f"Your current savings rate is {savings_pct:.1f}%. Look for small subscription cuts or dining adjustments to reach the 20% milestone."
                })
            else:
                insights.append({
                    'type': 'danger',
                    'icon': 'alert-octagon',
                    'title': 'Deficit Spending',
                    'message': f"Your expenses ({sym}{curr_spent:,.2f}) exceed your income ({sym}{curr_income:,.2f}) by {sym}{abs(savings):,.2f} this month. Review unnecessary costs."
                })

        # 5. Largest Transaction Alert
        largest_expense = Transaction.query.filter(
            Transaction.user_id == user_id,
            Transaction.type == 'expense',
            extract('month', Transaction.date) == current_month,
            extract('year', Transaction.date) == current_year
        ).order_by(Transaction.amount.desc()).first()

        if largest_expense and curr_spent > 0:
            pct_of_total = (largest_expense.amount / curr_spent) * 100
            if pct_of_total >= 25:
                insights.append({
                    'type': 'info',
                    'icon': 'zap',
                    'title': 'Single Major Expense',
                    'message': f"'{largest_expense.description}' ({sym}{largest_expense.amount:,.2f} in {largest_expense.category}) represents {pct_of_total:.1f}% of your total spending this month."
                })

        # Fallback if no transactions yet
        if not insights:
            insights.append({
                'type': 'info',
                'icon': 'info',
                'title': 'Welcome to Smart Expense Tracker!',
                'message': 'Add your first income or expense transaction to unlock personalized AI-driven financial insights and interactive spending charts.'
            })

        return insights
