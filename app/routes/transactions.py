import os
import sys
import csv
import io
from datetime import datetime, date, timedelta
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, Response
from flask_login import login_required, current_user
from sqlalchemy import or_

# Ensure project root is in sys.path if run directly
_PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from app.models import db, Transaction

transactions_bp = Blueprint('transactions', __name__, url_prefix='/transactions')


@transactions_bp.route('', methods=['GET'])
@login_required
def index():
    """Transactions listing with search, filtering, sorting, and pagination."""
    page = request.args.get('page', 1, type=int)
    per_page = 15

    # Filter parameters
    search_query = request.args.get('q', '').strip()
    trans_type = request.args.get('type', '').strip().lower()
    category = request.args.get('category', '').strip()
    timeframe = request.args.get('timeframe', 'all').strip()
    start_date_str = request.args.get('start_date', '').strip()
    end_date_str = request.args.get('end_date', '').strip()
    sort_by = request.args.get('sort', 'date_desc').strip()

    # Base query for current user
    query = Transaction.query.filter_by(user_id=current_user.id)

    # 1. Keyword search
    if search_query:
        query = query.filter(
            or_(
                Transaction.description.ilike(f'%{search_query}%'),
                Transaction.category.ilike(f'%{search_query}%'),
                Transaction.notes.ilike(f'%{search_query}%')
            )
        )

    # 2. Type filter
    if trans_type in ['income', 'expense']:
        query = query.filter(Transaction.type == trans_type)

    # 3. Category filter
    if category and category != 'All Categories':
        query = query.filter(Transaction.category == category)

    # 4. Date timeframe filter
    today = date.today()
    if timeframe == 'today':
        query = query.filter(Transaction.date == today)
    elif timeframe == 'this_week':
        start_of_week = today - timedelta(days=today.weekday())
        query = query.filter(Transaction.date >= start_of_week, Transaction.date <= today)
    elif timeframe == 'this_month':
        start_of_month = date(today.year, today.month, 1)
        query = query.filter(Transaction.date >= start_of_month, Transaction.date <= today)
    elif timeframe == 'this_year':
        start_of_year = date(today.year, 1, 1)
        query = query.filter(Transaction.date >= start_of_year, Transaction.date <= today)
    elif timeframe == 'custom':
        if start_date_str:
            try:
                start_dt = datetime.strptime(start_date_str, '%Y-%m-%d').date()
                query = query.filter(Transaction.date >= start_dt)
            except ValueError:
                pass
        if end_date_str:
            try:
                end_dt = datetime.strptime(end_date_str, '%Y-%m-%d').date()
                query = query.filter(Transaction.date <= end_dt)
            except ValueError:
                pass

    # 5. Sorting
    if sort_by == 'date_asc':
        query = query.order_by(Transaction.date.asc(), Transaction.id.asc())
    elif sort_by == 'amount_desc':
        query = query.order_by(Transaction.amount.desc())
    elif sort_by == 'amount_asc':
        query = query.order_by(Transaction.amount.asc())
    else:  # default date_desc
        query = query.order_by(Transaction.date.desc(), Transaction.id.desc())

    # Compute summary totals for the filtered results (all matching items)
    all_matching = query.all()
    filtered_income = sum(t.amount for t in all_matching if t.type == 'income')
    filtered_expense = sum(t.amount for t in all_matching if t.type == 'expense')
    filtered_net = filtered_income - filtered_expense

    # Paginate
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    transactions = pagination.items

    return render_template(
        'transactions/index.html',
        transactions=transactions,
        pagination=pagination,
        filtered_income=filtered_income,
        filtered_expense=filtered_expense,
        filtered_net=filtered_net,
        total_matching_count=len(all_matching),
        search_query=search_query,
        trans_type=trans_type,
        category=category,
        timeframe=timeframe,
        start_date_str=start_date_str,
        end_date_str=end_date_str,
        sort_by=sort_by
    )


@transactions_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    """Add a new transaction (supports standard form & AJAX)."""
    if request.method == 'POST':
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.is_json

        data = request.get_json() if request.is_json else request.form

        trans_type = data.get('type', 'expense').strip().lower()
        amount_val = data.get('amount')
        category = data.get('category', '').strip()
        description = data.get('description', '').strip()
        date_str = data.get('date', '').strip()
        payment_method = data.get('payment_method', 'Cash').strip()
        notes = data.get('notes', '').strip()

        errors = []

        if trans_type not in ['income', 'expense']:
            errors.append('Transaction type must be either Income or Expense.')

        try:
            amount = float(amount_val)
            if amount <= 0:
                errors.append('Amount must be greater than zero.')
        except (ValueError, TypeError):
            errors.append('Please enter a valid numeric amount.')

        if not category:
            errors.append('Please select a category.')

        if not description:
            errors.append('Please enter a description.')

        trans_date = date.today()
        if date_str:
            try:
                trans_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            except ValueError:
                errors.append('Invalid date format. Use YYYY-MM-DD.')

        if errors:
            if is_ajax:
                return jsonify({'success': False, 'errors': errors}), 400
            for err in errors:
                flash(err, 'danger')
            return render_template(
                'transactions/add.html',
                form_data=data,
                default_date=date.today().strftime('%Y-%m-%d')
            )

        new_trans = Transaction(
            user_id=current_user.id,
            type=trans_type,
            amount=amount,
            category=category,
            description=description,
            date=trans_date,
            payment_method=payment_method,
            notes=notes
        )
        db.session.add(new_trans)
        db.session.commit()

        if is_ajax:
            return jsonify({
                'success': True,
                'message': 'Transaction added successfully!',
                'transaction': new_trans.to_dict()
            })

        flash(f"{trans_type.capitalize()} of {current_user.currency_symbol}{amount:,.2f} added successfully!", 'success')
        return redirect(url_for('transactions.index'))

    return render_template(
        'transactions/add.html',
        default_date=date.today().strftime('%Y-%m-%d')
    )


@transactions_bp.route('/<int:trans_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(trans_id):
    """Edit an existing transaction."""
    transaction = Transaction.query.filter_by(id=trans_id, user_id=current_user.id).first_or_404()

    if request.method == 'POST':
        trans_type = request.form.get('type', 'expense').strip().lower()
        amount_val = request.form.get('amount')
        category = request.form.get('category', '').strip()
        description = request.form.get('description', '').strip()
        date_str = request.form.get('date', '').strip()
        payment_method = request.form.get('payment_method', 'Cash').strip()
        notes = request.form.get('notes', '').strip()

        errors = []

        if trans_type not in ['income', 'expense']:
            errors.append('Transaction type must be either Income or Expense.')

        try:
            amount = float(amount_val)
            if amount <= 0:
                errors.append('Amount must be greater than zero.')
        except (ValueError, TypeError):
            errors.append('Please enter a valid amount.')

        if not category:
            errors.append('Please select a category.')

        if not description:
            errors.append('Please enter a description.')

        trans_date = transaction.date
        if date_str:
            try:
                trans_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            except ValueError:
                errors.append('Invalid date format.')

        if errors:
            for err in errors:
                flash(err, 'danger')
            return render_template('transactions/edit.html', transaction=transaction)

        transaction.type = trans_type
        transaction.amount = amount
        transaction.category = category
        transaction.description = description
        transaction.date = trans_date
        transaction.payment_method = payment_method
        transaction.notes = notes

        db.session.commit()
        flash('Transaction updated successfully!', 'success')
        return redirect(url_for('transactions.index'))

    return render_template('transactions/edit.html', transaction=transaction)


@transactions_bp.route('/<int:trans_id>/delete', methods=['POST'])
@login_required
def delete(trans_id):
    """Delete a transaction."""
    transaction = Transaction.query.filter_by(id=trans_id, user_id=current_user.id).first_or_404()
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.is_json

    db.session.delete(transaction)
    db.session.commit()

    if is_ajax:
        return jsonify({'success': True, 'message': 'Transaction deleted.'})

    flash('Transaction deleted successfully.', 'info')
    return redirect(url_for('transactions.index'))


@transactions_bp.route('/export', methods=['GET'])
@login_required
def export_csv():
    """Exports all or filtered transactions to a CSV file."""
    # Build query matching user filters
    query = Transaction.query.filter_by(user_id=current_user.id)

    search_query = request.args.get('q', '').strip()
    trans_type = request.args.get('type', '').strip().lower()
    category = request.args.get('category', '').strip()

    if search_query:
        query = query.filter(
            or_(
                Transaction.description.ilike(f'%{search_query}%'),
                Transaction.category.ilike(f'%{search_query}%')
            )
        )
    if trans_type in ['income', 'expense']:
        query = query.filter(Transaction.type == trans_type)
    if category and category != 'All Categories':
        query = query.filter(Transaction.category == category)

    transactions = query.order_by(Transaction.date.desc()).all()

    output = io.StringIO()
    writer = csv.writer(output)

    # CSV Header
    writer.writerow(['ID', 'Date', 'Type', 'Category', 'Description', 'Amount', 'Currency', 'Payment Method', 'Notes'])

    for t in transactions:
        writer.writerow([
            t.id,
            t.date.strftime('%Y-%m-%d'),
            t.type.capitalize(),
            t.category,
            t.description,
            f"{t.amount:.2f}",
            current_user.currency,
            t.payment_method,
            t.notes or ''
        ])

    csv_data = output.getvalue()
    filename = f"transactions_{current_user.username}_{date.today().strftime('%Y%m%d')}.csv"

    return Response(
        csv_data,
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment;filename={filename}"}
    )
