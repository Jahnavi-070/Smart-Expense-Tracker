# 💰 Smart Expense Tracker

A modern, full-stack personal finance and expense tracking web application built with **Python (Flask)**, **SQLite**, **HTML5/CSS3/JavaScript**, and **Chart.js**.

Designed with a clean, portfolio-ready dark-glass UI, the application allows users to manage income and expenses, set monthly budgets with threshold alerts, visualize cashflow trends with interactive charts, and receive AI-driven financial insights.

---

## 🌟 Key Features

- **🔐 User Authentication & Profile**:
  - Secure registration and login with password hashing via `werkzeug.security`.
  - Session management via `Flask-Login` with `@login_required` route guards.
  - Multi-currency preference support (USD `$`, EUR `€`, GBP `£`, INR `₹`, CAD, AUD, JPY, AED, SGD, CHF, BRL, CNY, KRW, MXN).
  - **💱 Live Currency Conversion & Recalculation**: Option to automatically convert and recalculate all historical transaction amounts and budgets when changing currencies (e.g. converting between Rupees `₹` and Dollars `$`).
  - **Interactive Currency Converter Widget**: Live exchange rate calculation tool in settings.

- **📊 Comprehensive Financial Dashboard**:
  - Live metric cards: Net Balance, Total Income, Total Expenses, and Monthly Budget Progress.
  - **Interactive Chart.js Visualizations**:
    - **Category Breakdown Doughnut Chart**: Interactive hover tooltips and dynamic percentages.
    - **Monthly Cashflow Grouped Bar Chart**: Income vs. Expenses comparison across the past 6 months.
  - Quick-add transaction modal accessible from any page.
  - Recent activity feed with category badges and icons.

- **🤖 Smart Financial Insights Engine**:
  - Rule-based financial analysis that evaluates spending patterns, budget usage, savings rate, month-over-month (MoM) changes, and spending velocity.
  - Actionable recommendation alerts (Safe, Warning, Critical, Over-Budget).

- **💸 Transaction Management (Full CRUD)**:
  - Add, view, edit, and delete income and expense transactions.
  - Standard categories: `Food`, `Travel`, `Shopping`, `Bills`, `Education`, `Entertainment`, `Health`, `Other` (and income categories: `Salary`, `Freelance`, `Investments`, `Gift`, `Other`).
  - Payment method tagging (`Cash`, `Credit Card`, `Debit Card`, `UPI / Online`, `Bank Transfer`).
  - **Live Search & Multi-Criteria Filtering**: Filter by keyword, type, category, and date ranges (Today, This Week, This Month, This Year, or Custom Date Range).
  - **CSV Data Export**: Download filtered or complete transaction history as `.csv`.
  - Responsive pagination and dynamic sorting.

- **🎯 Monthly Budget Planner**:
  - Set overall monthly limits and individual category budgets.
  - Real-time progress bars with dynamic color-coded thresholds:
    - 🟢 `< 70%`: Normal / On Track
    - 🟡 `70% - 90%`: Warning
    - 🟠 `90% - 100%`: Critical Warning
    - 🔴 `> 100%`: Over-Budget Alert
  - Daily spending allowance calculation based on remaining days in the month.
  - "Copy Previous Month" feature to duplicate budgets with one click.

- **📈 Visual Analytics Hub**:
  - Deep-dive analytics page with multi-month cashflow comparisons.
  - Daily spending velocity area chart tracking cumulative day-by-day expenditure.
  - Category breakdown tables with visual share indicators.

- **📱 Responsive, Modern UI**:
  - Dark Slate & Indigo Glassmorphic design system.
  - Mobile drawer navigation and touch-friendly controls.

---

## 🛠️ Tech Stack

| Layer | Technology | Purpose |
| :--- | :--- | :--- |
| **Backend** | Python 3.10+, Flask 3.0+ | Application server, routing, REST APIs, business logic |
| **Database** | SQLite, Flask-SQLAlchemy | Relational data persistence with ORM models & foreign keys |
| **Authentication** | Flask-Login, Werkzeug | Session security, password hashing |
| **Frontend** | HTML5, CSS3, Vanilla JavaScript | Responsive modern UI with CSS variables & glassmorphism |
| **Visualizations** | Chart.js 4.4 | Doughnut, Bar, and Smooth Area Line charts |
| **Icons & Fonts** | Lucide Icons, Plus Jakarta Sans | Modern typography and UI iconography |
| **Testing** | `unittest` | Automated unit and integration test suite |
| **Version Control** | Git, GitHub | Source code management |

---

## 📁 Complete Project Structure

```
SmartExpenseTracker/
│
├── app/
│   ├── __init__.py               # Flask application factory, initializes SQLAlchemy & LoginManager
│   ├── config.py                 # Application settings, secret keys, categories & currencies
│   ├── models.py                 # SQLAlchemy database models: User, Transaction, Budget
│   │
│   ├── routes/
│   │   ├── __init__.py           # Blueprint package init
│   │   ├── auth.py               # Auth routes (register, login, logout, profile)
│   │   ├── dashboard.py          # Dashboard view and metric aggregations
│   │   ├── transactions.py       # Transaction CRUD, search, filter, pagination, CSV export
│   │   ├── budgets.py            # Budget planner, progress tracking, category limits
│   │   ├── analytics.py          # Visual analytics & deep-dive trends
│   │   └── api.py                # REST JSON endpoints for Chart.js charts & dynamic insights
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   └── insights_service.py   # Financial analytics and smart insight rule engine
│   │
│   ├── static/
│   │   ├── css/
│   │   │   ├── main.css          # Design system, CSS variables, glassmorphism, responsive grid
│   │   │   ├── dashboard.css     # Stat cards, insight cards, chart containers, recent activity
│   │   │   ├── transactions.css  # Transaction filter bar, data table, pagination, modals
│   │   │   ├── budgets.css       # Budget hero cards, category grid, progress thresholds
│   │   │   └── auth.css          # Authentication screen styling
│   │   │
│   │   ├── js/
│   │   │   ├── main.js           # Mobile drawer, toast alerts, global modals, AJAX quick-add
│   │   │   ├── dashboard.js      # Dashboard Chart.js rendering (Doughnut & Bar charts)
│   │   │   ├── transactions.js   # Dynamic category switching, date filters, delete handlers
│   │   │   ├── analytics.js      # Deep-dive analytics charts & velocity curves
│   │   │   └── budgets.js        # Budget presets and edit modal populator
│   │   │
│   │   └── images/
│   │       └── logo.svg          # Modern SVG app logo
│   │
│   └── templates/
│       ├── base.html             # Master layout with sidebar, topbar, toast alerts & modal
│       ├── auth/
│       │   ├── login.html        # Clean login page
│       │   ├── register.html     # Registration page with validation feedback
│       │   └── profile.html      # Account preferences and password update
│       ├── dashboard/
│       │   └── index.html        # Executive dashboard with stat cards, charts & insights
│       ├── transactions/
│       │   ├── index.html        # Transactions manager with filter toolbar & data table
│       │   ├── add.html          # Standalone add transaction form
│       │   └── edit.html         # Edit transaction form
│       ├── budgets/
│       │   └── index.html        # Monthly budget planner and progress meters
│       ├── analytics/
│       │   └── index.html        # Analytics page with time range filters & velocity chart
│       └── errors/
│           ├── 404.html          # Custom 404 Not Found page
│           └── 500.html          # Custom 500 Server Error page
│
├── tests/
│   ├── __init__.py
│   └── test_app.py               # Automated unit & integration tests
│
├── instance/                     # SQLite database directory (auto-created)
├── seed.py                       # Demo dataset generator (multi-month transactions & budgets)
├── run.py                        # Application entry point
├── requirements.txt              # Project Python dependencies
├── .gitignore                    # Python, SQLite, environment & cache ignore rules
└── README.md                     # Project documentation
```

---

## 🗄️ Database Schema

The SQLite database uses three normalized relational tables:

```
  +------------------+         +--------------------------+
  |      users       | 1     * |       transactions       |
  +------------------+---------+--------------------------+
  | id (PK)          |         | id (PK)                  |
  | username (UK)    |         | user_id (FK -> users.id) |
  | email (UK)       |         | type ('income'/'expense')|
  | password_hash    |         | amount (Float)           |
  | currency (Str)   |         | category (Str)           |
  | created_at (DT)  |         | description (Str)        |
  +------------------+         | date (Date)              |
           | 1                 | payment_method (Str)     |
           |                   | notes (Text)             |
           | *                 | created_at (DT)          |
  +------------------+         +--------------------------+
  |     budgets      |
  +------------------+
  | id (PK)          |
  | user_id (FK)     |
  | month (Int: 1-12)|
  | year (Int)       |
  | amount (Float)   |
  | category (Str)   |
  | created_at (DT)  |
  +------------------+
```

---

## 🚀 Getting Started

Follow these steps to set up and run Smart Expense Tracker locally:

### 1. Prerequisites
- Python 3.9 or higher installed on your system.
- Git installed.

### 2. Clone the Repository
```bash
git clone https://github.com/your-username/smart-expense-tracker.git
cd smart-expense-tracker
```

### 3. Create & Activate Virtual Environment
- **Windows (PowerShell):**
  ```powershell
  python -m venv venv
  .\venv\Scripts\Activate.ps1
  ```
- **macOS / Linux:**
  ```bash
  python3 -m venv venv
  source venv/bin/activate
  ```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. Seed Sample Data (Optional but Recommended)
Populate the database with realistic demo transactions and budgets across multiple months:
```bash
python seed.py
```

### 6. Run the Application
```bash
python run.py
```
Open your browser and navigate to: **`http://127.0.0.1:5000/`**

---

## 👤 Demo Login Credentials

If you ran `python seed.py`, you can log in immediately with:

- **Email:** `demo@example.com` (or username: `alex_finance`)
- **Password:** `password123`

You can also click **Create an Account** to register a fresh user.

---

## 🧪 Running Automated Tests

Run the comprehensive unit and integration test suite:

```bash
python -m unittest discover -s tests -p "test_*.py" -v
```

Tests cover:
- User registration, password hashing & login validation.
- Transaction CRUD, search, category filtering & CSV export.
- Budget progress calculations and threshold alerts.
- Dynamic Financial Insights engine accuracy.
- Chart.js JSON API response schemas.

---

## 📡 API Endpoints Overview

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/charts/category-expenses` | Category breakdown formatted for Chart.js Doughnut |
| `GET` | `/api/charts/monthly-cashflow` | Past N months income vs. expenses for Chart.js Bar chart |
| `GET` | `/api/charts/daily-spending` | Day-by-day and cumulative spending for Area Line chart |
| `GET` | `/api/insights` | Rule-based smart financial recommendations JSON |
| `GET` | `/api/summary` | Live summary metrics (Income, Expenses, Net Balance) |

---

## 📤 Uploading to GitHub

To push this project to your GitHub account:

```bash
git init
git add .
git commit -m "Initial commit: Smart Expense Tracker full-stack application"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/SmartExpenseTracker.git
git push -u origin main
```

---

## 📄 License

This project is open-source and available under the [MIT License](LICENSE).
