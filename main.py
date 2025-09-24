import mysql.connector
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import warnings
warnings.filterwarnings("ignore", category=UserWarning)


# ----------------------------
# Database Connection
# ----------------------------
def connect_db():
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="1234",
        database="finance_manager"
    )
    return conn


# ----------------------------
# USER MANAGEMENT
# ----------------------------
def add_user():
    name = input("Enter user name: ").strip()
    email = input("Enter email: ").strip()

    conn = connect_db()
    cursor = conn.cursor()

    # Check if email already exists
    cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
    existing = cursor.fetchone()

    if existing:
        print("\n❌  A user with this email already exists. Try again.")
    else:
        try:
            cursor.execute("INSERT INTO users (name,email) VALUES (%s,%s)", (name, email))
            conn.commit()
            print("\n✅  User added successfully!")
        except mysql.connector.Error as err:
            print("Error:\n", err)

    conn.close()

    # Always show updated user list
    list_users()

def list_users():
    conn = connect_db()
    df = pd.read_sql("SELECT * FROM users", conn)
    conn.close()

    if df.empty:
        print("\n⚠️  No users found. Please add a user first.")
    else:
        print("\n=== Users ===")
        print(df)


# ----------------------------
# CATEGORY MANAGEMENT
# ----------------------------
def add_category(return_id=False):
    name = input("Enter new category name: ").strip()
    if not name:
        print("\n❌  Category name cannot be empty!")
        return None
    
    conn = connect_db()
    cursor = conn.cursor()
    
    # Check if category already exists
    cursor.execute("SELECT * FROM categories WHERE name=%s", (name,))
    existing = cursor.fetchone()
    if existing:
        print("\n⚠️  Category already exists.")
        conn.close()
        if return_id:
            return existing[0]  # Return existing category_id
        return None
    
    try:
        cursor.execute("INSERT INTO categories (name) VALUES (%s)", (name,))
        conn.commit()
        category_id = cursor.lastrowid
        print(f"\n✅  Category '{name}' added successfully!")
        if return_id:
            return category_id
    except mysql.connector.Error as err:
        print("Error:\n", err)
        return None
    finally:
        conn.close()

def list_categories():
    conn = connect_db()
    df = pd.read_sql("SELECT * FROM categories", conn)
    print("\n",df)
    conn.close()


# ----------------------------
# INCOME & EXPENSE MANAGEMENT
# ----------------------------
def add_income():
    user_id = get_valid_user()
    if not user_id:
        return  # stop if no users exist

    amount = get_valid_amount()
    source = input("Enter income source: ").strip()
    date = get_valid_date()

    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO income (user_id, amount, source, date) VALUES (%s,%s,%s,%s)",
        (user_id, amount, source, date)
    )
    conn.commit()
    conn.close()

    print("\n✅  Income added!")

def add_expense():
    user_id = get_valid_user()
    if not user_id:
        return  # stop if no users exist

    amount = get_valid_amount()
    category_id = get_valid_category()
    if not category_id:
        return  # stop if no categories exist

    date = get_valid_date()

    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO expenses (user_id, amount, category_id, date) VALUES (%s,%s,%s,%s)",
        (user_id, amount, category_id, date)
    )
    conn.commit()
    conn.close()

    print("\n✅  Expense added!")


# ----------------------------
# DATA VALIDATION
# ----------------------------
def get_valid_amount():
    while True:
        try:
            amount = float(input("Enter amount: "))
            if amount <= 0:
                print("\n❌  Amount must be greater than 0.")
            else:
                return amount
        except ValueError:
            print("\n⚠️  Invalid amount! Please enter a number.")

def get_valid_date():
    while True:
        date_str = input("Enter date (YYYY-MM-DD): ")
        try:
            datetime.strptime(date_str, "%Y-%m-%d")  # check format
            return date_str
        except ValueError:
            print("\n⚠️  Invalid date format! Use YYYY-MM-DD.")

def get_valid_category():
    while True:
        conn = connect_db()
        df = pd.read_sql("SELECT * FROM categories", conn)
        conn.close()
        
        if df.empty:
            print("\n⚠️  No categories found. Please add a new category first.")
            new_id = add_category(return_id=True)
            return new_id
        
        print("\nAvailable Categories:")
        print(df)
        print("0 → Add a new category")

        try:
            category_id = int(input("\nEnter category ID (or 0 to add new): "))
            if category_id == 0:
                new_id = add_category(return_id=True)
                return new_id
            elif category_id in df['category_id'].values:
                return category_id
            else:
                print("\n❌  Invalid category ID. Choose from the list above or 0 to add new.")
        except ValueError:
            print("\n⚠️  Invalid input! Please enter a number.")

def get_valid_user():
    """Ensure the user enters a valid existing user_id."""
    conn = connect_db()
    df = pd.read_sql("SELECT * FROM users", conn)
    conn.close()

    if df.empty:
        print("\n⚠️  No users exist. Please add a user first.")
        return None  # Caller must handle this case

    while True:
        try:
            user_id = int(input("Enter user ID: "))
            if user_id in df['user_id'].values:
                return user_id
            else:
                print("\n❌  Invalid user ID. Please choose from the list below:")
                print(df[['user_id', 'name', 'email']])
        except ValueError:
            print("\n⚠️  Invalid input! Please enter a number.")
 

# ----------------------------
# ANALYTICS & VISUALIZATION
# ----------------------------
def monthly_summary(user_id):
    conn = connect_db()
    
    # Fetch income and expenses in a single SQL query each
    df_income = pd.read_sql(
        "SELECT amount, DATE_FORMAT(date, '%Y-%m') AS month FROM income WHERE user_id=%s",
        conn,
        params=(user_id,)
    )
    df_expenses = pd.read_sql(
        "SELECT amount, DATE_FORMAT(date, '%Y-%m') AS month FROM expenses WHERE user_id=%s",
        conn,
        params=(user_id,)
    )
    
    # Group by month and sum amounts
    income_summary = df_income.groupby('month')['amount'].sum()
    expenses_summary = df_expenses.groupby('month')['amount'].sum()
    
    # Combine into single DataFrame and calculate savings
    summary = pd.DataFrame({
        'Income': income_summary,
        'Expenses': expenses_summary
    }).fillna(0)
    
    summary['Savings'] = summary['Income'] - summary['Expenses']
    
    print(summary)
    return summary

def plot_expense_pie(user_id, month):
    conn = connect_db()
    
    query = """
        SELECT c.name, SUM(e.amount) as total
        FROM expenses e
        JOIN categories c ON e.category_id=c.category_id
        WHERE e.user_id=%s AND DATE_FORMAT(e.date,'%Y-%m')=%s
        GROUP BY c.name
    """
    df = pd.read_sql(query, conn, params=(user_id, month))
    
    # Simple matplotlib pie chart
    labels = df['name']
    sizes = df['total']
    
    plt.figure(figsize=(6,6))
    plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
    plt.title(f'Expenses for {month}')
    plt.axis('equal')  # Makes pie chart circular
    plt.show()

def plot_income_expense_trend(user_id):
    summary = monthly_summary(user_id)

    if summary.empty:
        print("\n⚠️ No income or expense records found for this user.")
        return

    # Ensure numeric types (sometimes SQL returns strings)
    summary = summary.astype(float)

    summary.plot(kind='line', marker='o', title='Income vs Expenses Trend')
    plt.xlabel("Month")
    plt.ylabel("Amount")
    plt.show()

def top_expense_categories(user_id, month):
    conn = connect_db()
    query = """
        SELECT c.name, SUM(e.amount) as total
        FROM expenses e
        JOIN categories c ON e.category_id = c.category_id
        WHERE e.user_id = %s AND DATE_FORMAT(e.date, '%Y-%m') = %s
        GROUP BY c.name
        ORDER BY total DESC
        LIMIT 3
    """
    df = pd.read_sql(query, conn, params=(user_id, month))
    conn.close()

    if df.empty:
        print(f"\n⚠️  No expenses found for {month}.")
        return None
    
    print("\nTop 3 Expense Categories for", month)
    print(df)

    # Optional: plot a bar chart
    df.plot(kind='bar', x='name', y='total', legend=False, title=f"Top 3 Expense Categories ({month})")
    plt.ylabel("Amount")
    plt.show()

    return df

def filter_records(user_id, record_type, filter_type, filter_value):
    conn = connect_db()
    cursor = conn.cursor()

    if record_type.lower() == "income":
        table = "income"
    elif record_type.lower() == "expense":
        table = "expenses"
    else:
        print("\n❌  Invalid record type. Choose 'income' or 'expense'.")
        return

    # Build SQL based on filter type
    if filter_type == "day":
        query = f"SELECT * FROM {table} WHERE user_id=%s AND DATE(date)=%s"
        params = (user_id, filter_value)
    elif filter_type == "month":
        query = f"SELECT * FROM {table} WHERE user_id = %s AND DATE_FORMAT(date, '%Y-%m') = %s"
        params = (user_id, filter_value)
    elif filter_type == "year":
        query = f"SELECT * FROM {table} WHERE user_id=%s AND YEAR(date)=%s"
        params = (user_id, filter_value)
    else:
        print("\n❌  Invalid filter type. Choose 'day', 'month', or 'year'.")
        return

    df = pd.read_sql(query, conn, params=params)
    conn.close()

    if df.empty:
        print(f"\n⚠️  No {record_type} records found for {filter_type}: {filter_value}")
    else:
        print(df)
    return df

def compare_months(user_id, month1, month2):
    conn = connect_db()

    query = """
        SELECT 'Income' AS type, DATE_FORMAT(date, '%Y-%m') AS month, SUM(amount) AS total
        FROM income
        WHERE user_id = %s AND DATE_FORMAT(date, '%Y-%m') IN (%s, %s)
        GROUP BY month
        UNION ALL
        SELECT 'Expenses' AS type, DATE_FORMAT(date, '%Y-%m') AS month, SUM(amount) AS total
        FROM expenses
        WHERE user_id = %s AND DATE_FORMAT(date, '%Y-%m') IN (%s, %s)
        GROUP BY month
    """

    df = pd.read_sql(query, conn, params=(user_id, month1, month2, user_id, month1, month2))
    conn.close()

    if df.empty:
        print("\n⚠️  No records found for the given months.")
        return

    # Pivot for better plotting
    pivot_df = df.pivot(index="type", columns="month", values="total").fillna(0)

    print("\nComparison Between Months:")
    print(pivot_df)

    # Bar chart
    pivot_df.plot(kind="bar", figsize=(7,5))
    plt.title(f"Income vs Expenses: {month1} vs {month2}")
    plt.ylabel("Amount")
    plt.show()


# ----------------------------
# DASHBOARD MENUS
# ----------------------------
def user_menu():
    while True:
        print("\n..................................................\n=== User Management ===\n")
        print("1. Add User")
        print("2. List Users")
        print("3. Back to Main Menu\n")
     
        choice = input("Enter choice: ")
       

        if choice == "1":
            add_user()
        elif choice == "2":
            list_users()
        elif choice == "3":
            break
        else:
            print("\n⚠️  Invalid choice! Try again.")

def category_menu():
    while True:
        print("\n..................................................\n=== Category Management ===\n")
        print("1. Add Category")
        print("2. List Categories")
        print("3. Back to Main Menu\n")
       
        choice = input("Enter choice: ")
      

        if choice == "1":
            add_category()
        elif choice == "2":
            list_categories()
        elif choice == "3":
            break
        else:
            print("\n⚠️  Invalid choice! Try again.")

def transaction_menu():
    while True:
        print("\n..................................................\n=== Transactions ===\n")
        print("1. Add Income")
        print("2. Add Expense")
        print("3. Back to Main Menu\n")
        
        choice = input("Enter choice: ")
        

        if choice == "1":
            add_income()
        elif choice == "2":
            add_expense()
        elif choice == "3":
            break
        else:
            print("\n⚠️  Invalid choice! Try again.")

def reports_menu():
    while True:
        print("\n..................................................\n=== Reports & Insights ===\n")
        print("1. Monthly Summary")
        print("2. Expense Pie Chart")
        print("3. Income vs Expenses Trend")
        print("4. Top 3 Expense Categories")
        print("5. Filter Records (by Date)")
        print("6. Compare Income & Expenses (Between Months)")
        print("7. Back to Main Menu\n")
        
        choice = input("Enter choice: ")
        

        if choice == "1":
            user_id = get_valid_user()
            if user_id: monthly_summary(user_id)
        elif choice == "2":
            user_id = get_valid_user()
            if user_id:
                month = input("Enter month (YYYY-MM): ")
                plot_expense_pie(user_id, month)
        elif choice == "3":
            user_id = get_valid_user()
            if user_id: plot_income_expense_trend(user_id)
        elif choice == "4":
            user_id = get_valid_user()
            if user_id:
                month = input("Enter month (YYYY-MM): ")
                top_expense_categories(user_id, month)
        elif choice == "5":
            user_id = get_valid_user()
            if user_id:
                record_type = input("Filter Income or Expense? ").strip().lower()
                filter_type = input("Filter by 'day', 'month', or 'year': ").strip().lower()
                filter_value = input("Enter value (YYYY-MM-DD / YYYY-MM / YYYY): ").strip()
                filter_records(user_id, record_type, filter_type, filter_value)
        elif choice == "6":
            user_id = get_valid_user()
            if user_id:
                month1 = input("Enter first month (YYYY-MM): ")
                month2 = input("Enter second month (YYYY-MM): ")
                compare_months(user_id, month1, month2)
        elif choice == "7":
            break
        else:
            print("\n⚠️  Invalid choice! Try again.")

def main_menu():
    while True:
        print("\n##################################################")
        print("\n=== Personal Finance Manager ===")
        print("1. User Management")
        print("2. Category Management")
        print("3. Transactions")
        print("4. Reports & Insights")
        print("5. Exit\n")
        choice = input("Enter your choice: ")

        if choice == "1":
            user_menu()
        elif choice == "2":
            category_menu()
        elif choice == "3":
            transaction_menu()
        elif choice == "4":
            reports_menu()
        elif choice == "5":
            print("\nExiting...\nThank you!\n\n")
            break
        else:
            print("\n⚠️  Invalid choice! Try again.")


# ----------------------------
# RUN THE PROGRAM
# ----------------------------
if __name__ == "__main__":
    main_menu()
