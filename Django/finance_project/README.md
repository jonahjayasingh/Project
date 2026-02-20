# Finance Project

A personal finance management application built with Django. This application helps users track their income, expenses, manage multiple accounts, and visualize their financial health through reports and dashboards.

## Features

- **User Authentication**: Secure registration and login system.
- **Dashboard**: A bird's-eye view of your total balance, recent transactions, and monthly income/expense summary.
- **Transaction Management**:
  - Add and track daily transactions (Income & Expense).
  - Categorize transactions for better organization.
  - Link transactions to specific accounts (Bank, Cash, etc.).
- **Account Management**:
  - Create and manage multiple financial accounts.
  - Automatic balance updates based on transactions.
  - Edit or delete accounts with balance recalculation.
- **Category Management**:
  - Custom categories for income and expenses.
  - Manage categories easily (Add, Edit, Delete).
- **Reports & Analytics**:
  - Visual reports for Income vs. Expense.
  - Category-wise spending breakdown.
  - Monthly trends (Last 6 months).
  - Filtering by account.
- **Data Export**: Export your transaction history to CSV for further analysis.
- **Responsive Design**: Built with Tailwind CSS for a modern and responsive user interface.

## Technologies Used

- **Backend**: Django 5.x
- **Frontend**: HTML5, Tailwind CSS
- **Database**: SQLite (Default)
- **Charts**: Chart.js (via JavaScript in templates)

## Getting Started

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

### Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd finance_project
   ```

2. **Create a virtual environment** (optional but recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install django
   ```

4. **Run Migrations**:
   ```bash
   python manage.py migrate
   ```

5. **Create a Superuser** (optional, for admin access):
   ```bash
   python manage.py createsuperuser
   ```

6. **Start the Development Server**:
   ```bash
   python manage.py runserver
   ```

7. **Access the Application**:
   Open your browser and Navigate to `http://127.0.0.1:8000/`.

## Usage

1. **Register** a new account or **Login**.
2. **Add Accounts** (e.g., Savings, Cash) to start tracking.
3. **Add Categories** to organize your transactions.
4. **Log Transactions** as they happen.
5. Check the **Dashboard** and **Reports** to monitor your progress.

## License

This project is licensed under the MIT License.
