import unittest
from datetime import date, datetime
from app import create_app
from app.config import TestConfig
from app.models import db, User, Transaction, Budget
from app.services.insights_service import FinancialInsightsService


class SmartExpenseTrackerTestCase(unittest.TestCase):
    """Test suite covering Authentication, Transactions, Budgets, and Insights."""

    def setUp(self):
        self.app = create_app(TestConfig)
        self.client = self.app.test_client()
        self.ctx = self.app.app_context()
        self.ctx.push()
        db.create_all()

        # Helper test user
        self.user = User(username='testuser', email='test@example.com', currency='USD')
        self.user.set_password('password123')
        db.session.add(self.user)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.ctx.pop()

    def login(self, identifier='testuser', password='password123'):
        return self.client.post('/login', data={
            'identifier': identifier,
            'password': password
        }, follow_redirects=True)

    def logout(self):
        return self.client.get('/logout', follow_redirects=True)

    # ----------------- Auth Tests -----------------
    def test_user_registration(self):
        """Test registering a new user."""
        res = self.client.post('/register', data={
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'secretpassword',
            'confirm_password': 'secretpassword',
            'currency': 'USD'
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Account created successfully', res.data)
        user = User.query.filter_by(username='newuser').first()
        self.assertIsNotNone(user)
        self.assertTrue(user.check_password('secretpassword'))

    def test_registration_password_mismatch(self):
        """Test registration failure on password mismatch."""
        res = self.client.post('/register', data={
            'username': 'mismatch',
            'email': 'mismatch@example.com',
            'password': 'password1',
            'confirm_password': 'password2',
            'currency': 'USD'
        }, follow_redirects=True)
        self.assertIn(b'Passwords do not match', res.data)

    def test_login_success_and_logout(self):
        """Test user login and session logout."""
        res = self.login('testuser', 'password123')
        self.assertIn(b'Welcome back, testuser', res.data)

        res_logout = self.logout()
        self.assertIn(b'You have been safely logged out', res_logout.data)

    def test_login_invalid_password(self):
        """Test invalid credentials rejection."""
        res = self.login('testuser', 'wrongpass')
        self.assertIn(b'Invalid username/email or password', res.data)

    # ----------------- Transaction Tests -----------------
    def test_add_transaction(self):
        """Test adding income and expense transactions."""
        self.login()
        res = self.client.post('/transactions/add', data={
            'type': 'expense',
            'amount': '45.50',
            'category': 'Food',
            'description': 'Lunch with Team',
            'date': date.today().strftime('%Y-%m-%d'),
            'payment_method': 'Credit Card',
            'notes': 'Team lunch'
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Expense of $45.50 added successfully', res.data)

        trans = Transaction.query.filter_by(user_id=self.user.id).first()
        self.assertIsNotNone(trans)
        self.assertEqual(trans.amount, 45.50)
        self.assertEqual(trans.category, 'Food')
        self.assertEqual(trans.type, 'expense')

    def test_edit_transaction(self):
        """Test editing an existing transaction."""
        self.login()
        t = Transaction(
            user_id=self.user.id,
            type='expense',
            amount=100.0,
            category='Shopping',
            description='Original Shoe',
            date=date.today(),
            payment_method='Cash'
        )
        db.session.add(t)
        db.session.commit()

        res = self.client.post(f'/transactions/{t.id}/edit', data={
            'type': 'expense',
            'amount': '120.00',
            'category': 'Shopping',
            'description': 'Updated Shoes with Tax',
            'date': date.today().strftime('%Y-%m-%d'),
            'payment_method': 'Credit Card',
            'notes': 'With warranty'
        }, follow_redirects=True)

        self.assertEqual(res.status_code, 200)
        updated = db.session.get(Transaction, t.id)
        self.assertEqual(updated.amount, 120.00)
        self.assertEqual(updated.description, 'Updated Shoes with Tax')

    def test_delete_transaction(self):
        """Test deleting a transaction."""
        self.login()
        t = Transaction(
            user_id=self.user.id,
            type='expense',
            amount=50.0,
            category='Bills',
            description='Electric Bill',
            date=date.today()
        )
        db.session.add(t)
        db.session.commit()

        res = self.client.post(f'/transactions/{t.id}/delete', follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIsNone(db.session.get(Transaction, t.id))

    def test_export_csv(self):
        """Test transactions CSV export."""
        self.login()
        t = Transaction(
            user_id=self.user.id,
            type='income',
            amount=2000.0,
            category='Salary',
            description='Monthly Pay',
            date=date.today()
        )
        db.session.add(t)
        db.session.commit()

        res = self.client.get('/transactions/export')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.mimetype, 'text/csv')
        self.assertIn(b'Monthly Pay', res.data)
        self.assertIn(b'Salary', res.data)

    # ----------------- Budget Tests -----------------
    def test_set_and_update_budget(self):
        """Test setting and updating budgets."""
        self.login()
        today = date.today()

        # Set overall budget
        res = self.client.post('/budgets/set', data={
            'month': today.month,
            'year': today.year,
            'amount': '1500',
            'category': 'overall'
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)

        b = Budget.query.filter_by(user_id=self.user.id, category=None).first()
        self.assertIsNotNone(b)
        self.assertEqual(b.amount, 1500.0)

        # Update budget
        self.client.post('/budgets/set', data={
            'month': today.month,
            'year': today.year,
            'amount': '1800',
            'category': 'overall'
        }, follow_redirects=True)

        updated_b = Budget.query.filter_by(user_id=self.user.id, category=None).first()
        self.assertEqual(updated_b.amount, 1800.0)

    # ----------------- Insights Service Tests -----------------
    def test_financial_insights_service(self):
        """Test calculation of financial metrics and insights."""
        today = date.today()

        # Add Income & Expenses
        db.session.add(Transaction(
            user_id=self.user.id,
            type='income',
            amount=5000.0,
            category='Salary',
            description='Salary',
            date=today
        ))
        db.session.add(Transaction(
            user_id=self.user.id,
            type='expense',
            amount=1200.0,
            category='Food',
            description='Groceries',
            date=today
        ))
        db.session.add(Transaction(
            user_id=self.user.id,
            type='expense',
            amount=300.0,
            category='Travel',
            description='Gas & Transit',
            date=today
        ))
        db.session.commit()

        metrics = FinancialInsightsService.get_summary_metrics(self.user.id, today)
        self.assertEqual(metrics['all_time_income'], 5000.0)
        self.assertEqual(metrics['all_time_expenses'], 1500.0)
        self.assertEqual(metrics['current_balance'], 3500.0)
        self.assertEqual(metrics['savings_rate'], 70.0)

        insights = FinancialInsightsService.generate_smart_insights(self.user.id)
        self.assertTrue(len(insights) > 0)

    # ----------------- API Endpoints Tests -----------------
    def test_api_category_chart(self):
        """Test JSON API for category chart."""
        self.login()
        res = self.client.get('/api/charts/category-expenses')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data['success'])
        self.assertIn('labels', data)
        self.assertIn('values', data)

    # ----------------- Currency Conversion Tests -----------------
    def test_currency_conversion(self):
        """Test converting user transaction data between currencies (USD -> INR)."""
        from app.services.currency_service import CurrencyService

        t = Transaction(
            user_id=self.user.id,
            type='expense',
            amount=100.0,
            category='Food',
            description='Dinner',
            date=date.today()
        )
        b = Budget(
            user_id=self.user.id,
            month=date.today().month,
            year=date.today().year,
            amount=1000.0
        )
        db.session.add_all([t, b])
        db.session.commit()

        # Convert from USD to INR
        t_count, b_count, rate = CurrencyService.convert_user_data(self.user, 'INR')
        self.assertEqual(t_count, 1)
        self.assertEqual(b_count, 1)
        self.assertEqual(self.user.currency, 'INR')
        self.assertEqual(self.user.currency_symbol, '₹')
        self.assertEqual(t.amount, 8350.0)
        self.assertEqual(b.amount, 83500.0)

    def test_api_currency_convert_endpoint(self):
        """Test /api/currency/convert endpoint."""
        self.login()
        res = self.client.get('/api/currency/convert?amount=100&from=USD&to=INR')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data['success'])
        self.assertEqual(data['converted_amount'], 8350.0)
        self.assertIn('₹', data['formatted'])


if __name__ == '__main__':
    unittest.main()

