import sqlite3
from typing import List, Dict, Tuple, Any, Optional
from datetime import datetime

DEFAULT_DB_PATH = "expense_tracker.db"

def get_connection(db_path: str = DEFAULT_DB_PATH) -> sqlite3.Connection:
    """
    Establishes and returns a connection to the SQLite database.
    Enforces foreign keys and configures row factory to return dictionary-like Row objects.
    """
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    # Enable foreign keys just in case relationships are added later
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def init_db(db_path: str = DEFAULT_DB_PATH) -> None:
    """
    Creates tables for income, expenses, budgets, and savings goals if they do not exist.
    """
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        
        # 1. Income Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS income (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                amount REAL NOT NULL,
                category TEXT NOT NULL,
                subcategory TEXT,
                description TEXT,
                date TEXT NOT NULL
            );
        """)
        
        # 2. Expenses Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                amount REAL NOT NULL,
                category TEXT NOT NULL,
                subcategory TEXT,
                description TEXT,
                date TEXT NOT NULL,
                tag TEXT,
                repeating_interval TEXT DEFAULT 'none'
            );
        """)
        
        # 3. Budgets Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS budgets (
                category TEXT PRIMARY KEY,
                allocated_amount REAL NOT NULL
            );
        """)
        
        # 4. Savings Goals Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS savings_goals (
                month TEXT PRIMARY KEY, -- Format: YYYY-MM
                target_amount REAL NOT NULL
            );
        """)
        
        conn.commit()

# --- INSERT OPERATIONS ---

def insert_income(
    amount: float,
    category: str,
    subcategory: Optional[str],
    description: Optional[str],
    date: str,
    db_path: str = DEFAULT_DB_PATH
) -> int:
    """
    Inserts a new record into the income table.
    Returns the auto-generated id of the newly inserted row.
    """
    query = """
        INSERT INTO income (amount, category, subcategory, description, date)
        VALUES (?, ?, ?, ?, ?);
    """
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(query, (amount, category, subcategory, description, date))
        conn.commit()
        return cursor.lastrowid

def insert_expense(
    amount: float,
    category: str,
    subcategory: Optional[str],
    description: Optional[str],
    date: str,
    tag: Optional[str],
    repeating_interval: Optional[str] = "none",
    db_path: str = DEFAULT_DB_PATH
) -> int:
    """
    Inserts a new record into the expenses table.
    Returns the auto-generated id of the newly inserted row.
    """
    query = """
        INSERT INTO expenses (amount, category, subcategory, description, date, tag, repeating_interval)
        VALUES (?, ?, ?, ?, ?, ?, ?);
    """
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(query, (
            amount, 
            category, 
            subcategory, 
            description, 
            date, 
            tag, 
            repeating_interval if repeating_interval else "none"
        ))
        conn.commit()
        return cursor.lastrowid

# --- READ OPERATIONS ---

def fetch_all_transactions(db_path: str = DEFAULT_DB_PATH) -> List[Dict[str, Any]]:
    """
    Fetches all income and expense entries, merges them, and returns a unified 
    chronological list of transactions sorted by date descending.
    Each transaction dictionary contains a 'type' key ('income' or 'expense').
    """
    transactions = []
    
    with get_connection(db_path) as conn:
        # Fetch income records
        income_rows = conn.execute(
            "SELECT id, amount, category, subcategory, description, date FROM income"
        ).fetchall()
        for row in income_rows:
            tx = dict(row)
            tx['type'] = 'income'
            tx['tag'] = None
            tx['repeating_interval'] = None
            transactions.append(tx)
            
        # Fetch expense records
        expense_rows = conn.execute(
            "SELECT id, amount, category, subcategory, description, date, tag, repeating_interval FROM expenses"
        ).fetchall()
        for row in expense_rows:
            tx = dict(row)
            tx['type'] = 'expense'
            transactions.append(tx)
            
    # Sort transactions by date descending, then ID descending
    transactions.sort(key=lambda x: (x['date'], x['id']), reverse=True)
    return transactions

def calculate_current_balances(db_path: str = DEFAULT_DB_PATH) -> Dict[str, float]:
    """
    Calculates total income, total expenses, and the current net balance.
    """
    with get_connection(db_path) as conn:
        total_income_row = conn.execute("SELECT SUM(amount) as total FROM income;").fetchone()
        total_expenses_row = conn.execute("SELECT SUM(amount) as total FROM expenses;").fetchone()
        
        total_income = total_income_row['total'] if total_income_row['total'] is not None else 0.0
        total_expenses = total_expenses_row['total'] if total_expenses_row['total'] is not None else 0.0
        
        return {
            "total_income": total_income,
            "total_expenses": total_expenses,
            "net_balance": total_income - total_expenses
        }

def fetch_category_spending_totals(db_path: str = DEFAULT_DB_PATH) -> Dict[str, float]:
    """
    Fetches the total amount spent grouped by expense category.
    Returns a dictionary mapping category names to their respective total spending.
    """
    query = """
        SELECT category, SUM(amount) as total 
        FROM expenses 
        GROUP BY category
        ORDER BY total DESC;
    """
    category_totals = {}
    with get_connection(db_path) as conn:
        rows = conn.execute(query).fetchall()
        for row in rows:
            category_totals[row['category']] = row['total']
    return category_totals

# --- BUDGETS & SAVINGS GOALS HELPER OPERATIONS ---

def set_budget(category: str, allocated_amount: float, db_path: str = DEFAULT_DB_PATH) -> None:
    """
    Sets or updates a budget for a category.
    """
    query = """
        INSERT INTO budgets (category, allocated_amount)
        VALUES (?, ?)
        ON CONFLICT(category) DO UPDATE SET allocated_amount = excluded.allocated_amount;
    """
    with get_connection(db_path) as conn:
        conn.execute(query, (category, allocated_amount))
        conn.commit()

def fetch_all_budgets(db_path: str = DEFAULT_DB_PATH) -> Dict[str, float]:
    """
    Fetches all budgets.
    Returns a dictionary mapping category to allocated_amount.
    """
    budgets = {}
    with get_connection(db_path) as conn:
        rows = conn.execute("SELECT category, allocated_amount FROM budgets;").fetchall()
        for row in rows:
            budgets[row['category']] = row['allocated_amount']
    return budgets

def set_savings_goal(month: str, target_amount: float, db_path: str = DEFAULT_DB_PATH) -> None:
    """
    Sets or updates a savings goal for a given month (format: YYYY-MM).
    """
    query = """
        INSERT INTO savings_goals (month, target_amount)
        VALUES (?, ?)
        ON CONFLICT(month) DO UPDATE SET target_amount = excluded.target_amount;
    """
    with get_connection(db_path) as conn:
        conn.execute(query, (month, target_amount))
        conn.commit()

def fetch_all_savings_goals(db_path: str = DEFAULT_DB_PATH) -> Dict[str, float]:
    """
    Fetches all savings goals.
    Returns a dictionary mapping month (YYYY-MM) to target_amount.
    """
    goals = {}
    with get_connection(db_path) as conn:
        rows = conn.execute("SELECT month, target_amount FROM savings_goals;").fetchall()
        for row in rows:
            goals[row['month']] = row['target_amount']
    return goals

# --- DELETE OPERATIONS ---

def delete_income(income_id: int, db_path: str = DEFAULT_DB_PATH) -> bool:
    """
    Deletes an income entry by its ID. Returns True if a record was deleted, False otherwise.
    """
    with get_connection(db_path) as conn:
        cursor = conn.execute("DELETE FROM income WHERE id = ?;", (income_id,))
        conn.commit()
        return cursor.rowcount > 0

def delete_expense(expense_id: int, db_path: str = DEFAULT_DB_PATH) -> bool:
    """
    Deletes an expense entry by its ID. Returns True if a record was deleted, False otherwise.
    """
    with get_connection(db_path) as conn:
        cursor = conn.execute("DELETE FROM expenses WHERE id = ?;", (expense_id,))
        conn.commit()
        return cursor.rowcount > 0

# --- INITIALIZE DATABASE ON MODULE LOAD (IF RUN DIRECTLY) ---
if __name__ == "__main__":
    print("Initializing SQLite database 'expense_tracker.db'...")
    init_db()
    print("Database and tables successfully initialized.")
    
    # Simple verification test run
    test_income_id = insert_income(5000.0, "Salary", "Primary", "Monthly paycheck", "2026-06-01")
    test_expense_id = insert_expense(1200.0, "Housing", "Rent", "June Rent Payment", "2026-06-02", "fixed", "monthly")
    
    set_budget("Housing", 1500.0)
    set_savings_goal("2026-06", 2000.0)
    
    balances = calculate_current_balances()
    print(f"Current Balances Test: {balances}")
    
    transactions = fetch_all_transactions()
    print(f"Transactions Fetched: {len(transactions)} entries found.")
    
    spending = fetch_category_spending_totals()
    print(f"Category Spending Totals: {spending}")
    
    # Cleanup test entries
    delete_income(test_income_id)
    delete_expense(test_expense_id)
    print("Database test run complete and temporary rows cleaned up!")
