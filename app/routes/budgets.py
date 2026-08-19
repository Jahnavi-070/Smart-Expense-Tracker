from datetime import date
from calendar import monthrange
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from sqlalchemy import func, extract
from app.models import db, Budget, Transaction
from app.config import Config

budgets_bp = Blueprint('budgets', __name__, url_prefix='/budgets')


@budgets_bp.route('', methods=['GET'])
@login_required
def index():
    """Monthly budget manager and progress tracking."""
    today = date.today()
    month = request.args.get('month', today.month, type=int)
    year = request.args.get('year', today.year, type=int)

    # Days calculation
    days_in_month = monthrange(year, month)[1]
    is_current_month = (year == today.year and month == today.month)
    days_remaining = max(1, days_in_month - today.day) if is_current_month else (days_in_month if (year > today.year or (year == today.year and month > today.month)) else 0)

    # Fetch user's overall budget for target month/year
    overall_budget = Budget.query.filter_by(
        user_id=current_user.id,
        month=month,
        year=year,
        category=None
    ).first()

    # Total month expenses
    total_month_spent = db.session.query(func.coalesce(func.sum(Transaction.amount), 0.0)).filter(
        Transaction.user_id == current_user.id,
        Transaction.type == 'expense',
        extract('month', Transaction.date) == month,
        extract('year', Transaction.date) == year
    ).scalar()

    overall_data = None
    if overall_budget:
        budget_amt = overall_budget.amount
        pct = (total_month_spent / budget_amt * 100) if budget_amt > 0 else 0
        rem = budget_amt - total_month_spent
        daily_lim = (rem / days_remaining) if days_remaining > 0 and rem > 0 else 0.0
        
        status = 'normal'
        if pct > 100:
            status = 'overbudget'
        elif pct >= 90:
            status = 'danger'
        elif pct >= 70:
            status = 'warning'

        overall_data = {
            'budget': overall_budget,
            'amount': budget_amt,
            'spent': total_month_spent,
            'remaining': rem,
            'percentage': round(pct, 1),
            'progress_percent': min(100.0, round(pct, 1)),
            'daily_limit': round(daily_lim, 2),
            'status': status
        }

    # Category Budgets for this month
    category_budgets = Budget.query.filter(
        Budget.user_id == current_user.id,
        Budget.month == month,
        Budget.year == year,
        Budget.category.isnot(None)
    ).all()

    category_items = []
    for cb in category_budgets:
        spent = db.session.query(func.coalesce(func.sum(Transaction.amount), 0.0)).filter(
            Transaction.user_id == current_user.id,
            Transaction.type == 'expense',
            Transaction.category == cb.category,
            extract('month', Transaction.date) == month,
            extract('year', Transaction.date) == year
        ).scalar()

        pct = (spent / cb.amount * 100) if cb.amount > 0 else 0
        rem = cb.amount - spent

        status = 'normal'
        if pct > 100:
            status = 'overbudget'
        elif pct >= 90:
            status = 'danger'
        elif pct >= 70:
            status = 'warning'

        category_items.append({
            'budget': cb,
            'category': cb.category,
            'amount': cb.amount,
            'spent': spent,
            'remaining': rem,
            'percentage': round(pct, 1),
            'progress_percent': min(100.0, round(pct, 1)),
            'status': status
        })

    # Available expense categories that don't have a category budget yet
    set_categories = {cb.category for cb in category_budgets}
    available_categories = [c for c in Config.EXPENSE_CATEGORIES if c not in set_categories]

    month_name = date(year, month, 1).strftime('%B %Y')

    return render_template(
        'budgets/index.html',
        month=month,
        year=year,
        month_name=month_name,
        overall_data=overall_data,
        category_items=category_items,
        available_categories=available_categories,
        days_remaining=days_remaining,
        is_current_month=is_current_month,
        today=today
    )


@budgets_bp.route('/set', methods=['POST'])
@login_required
def set_budget():
    """Create or update an overall or category-level budget."""
    try:
        month = int(request.form.get('month', date.today().month))
        year = int(request.form.get('year', date.today().year))
        amount = float(request.form.get('amount', 0))
        category = request.form.get('category', '').strip()
        if category == 'overall' or not category:
            category = None

        if amount <= 0:
            flash('Budget amount must be greater than zero.', 'danger')
            return redirect(url_for('budgets.index', month=month, year=year))

        # Check existing budget
        existing = Budget.query.filter_by(
            user_id=current_user.id,
            month=month,
            year=year,
            category=category
        ).first()

        if existing:
            existing.amount = amount
            flash(f"Budget for {category or 'Overall'} updated to {current_user.currency_symbol}{amount:,.2f}.", 'success')
        else:
            new_budget = Budget(
                user_id=current_user.id,
                month=month,
                year=year,
                amount=amount,
                category=category
            )
            db.session.add(new_budget)
            flash(f"Budget of {current_user.currency_symbol}{amount:,.2f} set for {category or 'Overall'}.", 'success')

        db.session.commit()
    except (ValueError, TypeError):
        flash('Invalid budget parameters submitted.', 'danger')

    return redirect(url_for('budgets.index', month=month, year=year))


@budgets_bp.route('/<int:budget_id>/delete', methods=['POST'])
@login_required
def delete_budget(budget_id):
    """Delete a budget."""
    budget = Budget.query.filter_by(id=budget_id, user_id=current_user.id).first_or_404()
    month, year = budget.month, budget.year
    db.session.delete(budget)
    db.session.commit()
    flash('Budget removed successfully.', 'info')
    return redirect(url_for('budgets.index', month=month, year=year))


@budgets_bp.route('/copy-previous', methods=['POST'])
@login_required
def copy_previous():
    """Copies all budgets from previous month into current month."""
    today = date.today()
    curr_month = int(request.form.get('month', today.month))
    curr_year = int(request.form.get('year', today.year))

    prev_month = curr_month - 1 if curr_month > 1 else 12
    prev_year = curr_year if curr_month > 1 else curr_year - 1

    prev_budgets = Budget.query.filter_by(
        user_id=current_user.id,
        month=prev_month,
        year=prev_year
    ).all()

    if not prev_budgets:
        flash(f"No budgets found in previous month ({date(prev_year, prev_month, 1).strftime('%B %Y')}) to copy.", 'warning')
        return redirect(url_for('budgets.index', month=curr_month, year=curr_year))

    copied_count = 0
    for pb in prev_budgets:
        existing = Budget.query.filter_by(
            user_id=current_user.id,
            month=curr_month,
            year=curr_year,
            category=pb.category
        ).first()

        if not existing:
            new_b = Budget(
                user_id=current_user.id,
                month=curr_month,
                year=curr_year,
                amount=pb.amount,
                category=pb.category
            )
            db.session.add(new_b)
            copied_count += 1

    db.session.commit()
    flash(f"Successfully copied {copied_count} budget limits from previous month!", 'success')
    return redirect(url_for('budgets.index', month=curr_month, year=curr_year))
