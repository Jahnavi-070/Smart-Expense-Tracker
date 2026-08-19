import os
from datetime import date, timedelta
from app import create_app
from app.models import db, User, Transaction, Budget

app = create_app()

def seed_database():
    """Populates the database with a rich demo user dataset for portfolio presentation."""
    with app.app_context():
        # Ensure tables exist
        db.create_all()

        demo_email = "demo@example.com"
        demo_username = "alex_finance"
        demo_password = "password123"

        user = User.query.filter_by(email=demo_email).first()
        if user:
            print(f"[!] Demo user '{demo_email}' already exists. Deleting existing transactions & budgets to refresh...")
            Transaction.query.filter_by(user_id=user.id).delete()
            Budget.query.filter_by(user_id=user.id).delete()
            db.session.commit()
        else:
            print(f"[+] Creating demo user: {demo_email}...")
            user = User(
                username=demo_username,
                email=demo_email,
                currency="USD"
            )
            user.set_password(demo_password)
            db.session.add(user)
            db.session.commit()

        today = date.today()
        transactions_to_add = []

        # Helper to generate dates relative to current month
        def make_date(months_ago, day):
            calc_year = today.year
            calc_month = today.month - months_ago
            while calc_month <= 0:
                calc_month += 12
                calc_year -= 1
            # Bound day to max days in month
            from calendar import monthrange
            max_d = monthrange(calc_year, calc_month)[1]
            return date(calc_year, calc_month, min(day, max_d))

        print("[+] Generating multi-month financial transactions...")

        # Past 4 months data
        for m in range(3, -1, -1):
            # Monthly Income
            transactions_to_add.append(Transaction(
                user_id=user.id,
                type="income",
                amount=4200.00,
                category="Salary",
                description="Monthly Tech Job Salary",
                date=make_date(m, 1),
                payment_method="Bank Transfer",
                notes="Direct deposit from Acme Corp"
            ))

            transactions_to_add.append(Transaction(
                user_id=user.id,
                type="income",
                amount=650.00,
                category="Freelance",
                description="Frontend UI Design Project",
                date=make_date(m, 14),
                payment_method="UPI / Online",
                notes="Client milestone payout"
            ))

            # Fixed Bills
            transactions_to_add.append(Transaction(
                user_id=user.id,
                type="expense",
                amount=1200.00,
                category="Bills",
                description="Apartment Rent",
                date=make_date(m, 2),
                payment_method="Bank Transfer",
                notes="Monthly lease"
            ))

            transactions_to_add.append(Transaction(
                user_id=user.id,
                type="expense",
                amount=95.00,
                category="Bills",
                description="Fiber High-Speed Internet",
                date=make_date(m, 4),
                payment_method="Credit Card",
                notes="Home broadband"
            ))

            transactions_to_add.append(Transaction(
                user_id=user.id,
                type="expense",
                amount=65.00,
                category="Bills",
                description="Electricity & Utility Bill",
                date=make_date(m, 7),
                payment_method="Debit Card",
                notes="City Power"
            ))

            # Food & Groceries
            transactions_to_add.append(Transaction(
                user_id=user.id,
                type="expense",
                amount=145.50,
                category="Food",
                description="Whole Foods Organic Market",
                date=make_date(m, 5),
                payment_method="Credit Card",
                notes="Weekly household groceries"
            ))

            transactions_to_add.append(Transaction(
                user_id=user.id,
                type="expense",
                amount=42.80,
                category="Food",
                description="Dinner with friends at Chipotle",
                date=make_date(m, 9),
                payment_method="UPI / Online",
                notes="Burrito bowls"
            ))

            transactions_to_add.append(Transaction(
                user_id=user.id,
                type="expense",
                amount=128.20,
                category="Food",
                description="Trader Joe's Grocery Restock",
                date=make_date(m, 18),
                payment_method="Debit Card",
                notes="Pantry staples & fruits"
            ))

            transactions_to_add.append(Transaction(
                user_id=user.id,
                type="expense",
                amount=34.00,
                category="Food",
                description="Coffee & Bakery Breakfast",
                date=make_date(m, 22),
                payment_method="Cash",
                notes="Morning brew"
            ))

            # Travel & Commute
            transactions_to_add.append(Transaction(
                user_id=user.id,
                type="expense",
                amount=75.00,
                category="Travel",
                description="Metro Transit Monthly Pass",
                date=make_date(m, 3),
                payment_method="Debit Card",
                notes="City subway"
            ))

            transactions_to_add.append(Transaction(
                user_id=user.id,
                type="expense",
                amount=48.50,
                category="Travel",
                description="Uber Ride to Airport",
                date=make_date(m, 16),
                payment_method="Credit Card",
                notes="Late night ride"
            ))

            # Entertainment & Subscriptions
            transactions_to_add.append(Transaction(
                user_id=user.id,
                type="expense",
                amount=22.99,
                category="Entertainment",
                description="Netflix 4K & Spotify Family",
                date=make_date(m, 10),
                payment_method="Credit Card",
                notes="Auto-recurring digital subscriptions"
            ))

            transactions_to_add.append(Transaction(
                user_id=user.id,
                type="expense",
                amount=55.00,
                category="Entertainment",
                description="Weekend IMAX Movie Tickets",
                date=make_date(m, 20),
                payment_method="Credit Card",
                notes="Popcorn & tickets"
            ))

            # Health & Fitness
            transactions_to_add.append(Transaction(
                user_id=user.id,
                type="expense",
                amount=60.00,
                category="Health",
                description="Gym & Fitness Membership",
                date=make_date(m, 6),
                payment_method="Credit Card",
                notes="Monthly club access"
            ))

            # Education & Self-Improvement
            transactions_to_add.append(Transaction(
                user_id=user.id,
                type="expense",
                amount=39.99,
                category="Education",
                description="O'Reilly Books & Online Course",
                date=make_date(m, 12),
                payment_method="UPI / Online",
                notes="Python & Cloud Architecture course"
            ))

            # Shopping
            transactions_to_add.append(Transaction(
                user_id=user.id,
                type="expense",
                amount=119.00,
                category="Shopping",
                description="Nike Running Sneakers",
                date=make_date(m, 15),
                payment_method="Credit Card",
                notes="Seasonal shoe sale"
            ))

        # Add single large expense in current month for AI insight demo
        transactions_to_add.append(Transaction(
            user_id=user.id,
            type="expense",
            amount=280.00,
            category="Shopping",
            description="UltraWide 4K Monitor Upgrade",
            date=make_date(0, min(today.day, 12)),
            payment_method="Credit Card",
            notes="Productivity workstation setup"
        ))

        db.session.add_all(transactions_to_add)

        # Set Budgets for current month & previous month
        print("[+] Configuring sample monthly budgets...")
        for m in [0, 1]:
            calc_year = today.year
            calc_month = today.month - m
            while calc_month <= 0:
                calc_month += 12
                calc_year -= 1

            budgets = [
                Budget(user_id=user.id, month=calc_month, year=calc_year, amount=3200.00, category=None),
                Budget(user_id=user.id, month=calc_month, year=calc_year, amount=550.00, category="Food"),
                Budget(user_id=user.id, month=calc_month, year=calc_year, amount=300.00, category="Shopping"),
                Budget(user_id=user.id, month=calc_month, year=calc_year, amount=200.00, category="Travel"),
                Budget(user_id=user.id, month=calc_month, year=calc_year, amount=150.00, category="Entertainment"),
                Budget(user_id=user.id, month=calc_month, year=calc_year, amount=1400.00, category="Bills"),
            ]
            db.session.add_all(budgets)

        db.session.commit()

        print("\n==============================================================")
        print(" [SUCCESS] Database seeded successfully!")
        print("==============================================================")
        print(f" Demo User Email:    {demo_email}")
        print(f" Demo User Password: {demo_password}")
        print(f" Transactions Added: {len(transactions_to_add)}")
        print("==============================================================")
        print(" Run 'python run.py' and login to explore the full dashboard!\n")

if __name__ == '__main__':
    seed_database()
