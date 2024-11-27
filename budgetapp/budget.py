import sqlite3
from datetime import datetime

# Connect to SQLite database (it will create the file if it doesn't exist)
conn = sqlite3.connect('budget_tracker.db')
cursor = conn.cursor()

# Create tables for expenses and income with larger categories
cursor.execute('''
CREATE TABLE IF NOT EXISTS expenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    description TEXT NOT NULL,
    amount REAL NOT NULL,
    category TEXT NOT NULL,
    larger_category TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    feeling INTEGER CHECK(feeling >= 1 AND feeling <= 5)  -- Feeling scale from 1 to 5
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS income (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    amount REAL NOT NULL,
    category TEXT NOT NULL,
    timestamp TEXT NOT NULL
)
''')

# Function to get the current balance
def get_current_balance():
    cursor.execute("SELECT SUM(amount) FROM income")
    total_income = cursor.fetchone()[0] or 0
    cursor.execute("SELECT SUM(amount) FROM expenses")
    total_expenses = cursor.fetchone()[0] or 0
    return total_income - total_expenses

# Function to add an expense with a larger category and feeling scale
def add_expense(description, amount, category, larger_category, feeling):
    if larger_category not in ['Essentials', 'Personal', 'Leisure', 'Investment']:
        print("Invalid larger category. Allowed categories are: Essentials, Personal, Leisure, Investment.")
        return False  # Return False to indicate an invalid category
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute('''
    INSERT INTO expenses (description, amount, category, larger_category, timestamp, feeling)
    VALUES (?, ?, ?, ?, ?, ?)
    ''', (description, amount, category, larger_category, timestamp, feeling))
    conn.commit()
    print(f"Expense added! Current balance: KES {get_current_balance():.2f}")
    return True  # Return True to indicate successful addition

# Function to add income with specific categories
def add_income(amount, category):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute('''
    INSERT INTO income (amount, category, timestamp)
    VALUES (?, ?, ?)
    ''', (amount, category, timestamp))
    conn.commit()
    print(f"Income added! Current balance: KES {get_current_balance():.2f}")

# Function to view previous expenses
def view_expenses():
    cursor.execute("SELECT * FROM expenses ORDER BY timestamp DESC")
    rows = cursor.fetchall()
    if not rows:
        print("No expenses recorded.")
        return
    print("Expenses:")
    for row in rows:
        print(f"Description: {row[1]} | Amount: KES {row[2]:.2f} | Category: {row[3]} | Larger Category: {row[4]} | Date: {row[5]} | Feeling: {row[6]}")

# Function to view previous income
def view_income():
    cursor.execute("SELECT * FROM income ORDER BY timestamp DESC")
    rows = cursor.fetchall()
    if not rows:
        print("No income recorded.")
        return
    print("Income:")
    for row in rows:
        print(f"Amount: KES {row[1]:.2f} | Category: {row[2]} | Date: {row[3]}")
    print(f"Current balance: KES {get_current_balance():.2f}")


# Simple command-line interface for interacting with the tracker
def main():
    while True:
        print("\nMinimalist Budget Tracker")
        print("1. Add Expense")
        print("2. Add Income")
        print("3. View Expenses")
        print("4. View Income")
        print("5. Exit")

        choice = input("Enter an option (1-5): ")

        if choice == '1':
            description = input("Enter expense description: ")
            
            # Loop until a valid numeric amount is entered
            while True:
                try:
                    amount = float(input("Enter expense amount: "))
                    if amount <= 0:
                        print("Amount must be a positive number.")
                    else:
                        break  # Exit the loop if a valid number is entered
                except ValueError:
                    print("Invalid input. Please enter a valid number for the amount.")

            category = input("Enter expense category (e.g., Internet, Rent, Food): ")
            
            # Loop until a valid larger category is entered
            while True:
                larger_category = input("Enter larger category (Essentials, Personal, Leisure, Investment): ")
                if larger_category not in ['Essentials', 'Personal', 'Leisure', 'Investment']:
                    print("Invalid larger category. Allowed categories are: Essentials, Personal, Leisure, Investment.")
                else:
                    break  # Exit the loop if a valid category is entered

            # Loop until a valid feeling scale is entered
            while True:
                try:
                    feeling = int(input("On a scale of 1 to 5, how do you feel about this expense? (1 = very negative, 5 = very positive): "))
                    if feeling < 1 or feeling > 5:
                        print("Invalid feeling scale. Please enter a value between 1 and 5.")
                    else:
                        break  # Exit the loop if a valid feeling scale is entered
                except ValueError:
                    print("Invalid input. Please enter a numeric value between 1 and 5.")
            
            # Call add_expense and check if the category was valid
            if add_expense(description, amount, category, larger_category, feeling) is False:
                print("Expense not added due to invalid category.")

        elif choice == '2':
            # Loop until a valid numeric amount is entered for income
            while True:
                try:
                    amount = float(input("Enter income amount: "))
                    if amount <= 0:
                        print("Amount must be a positive number.")
                    else:
                        break  # Exit the loop if a valid number is entered
                except ValueError:
                    print("Invalid input. Please enter a valid number for the income amount.")
                    
            category = input("Enter income category (e.g., Family, Freelance, Business): ")
            add_income(amount, category)

        elif choice == '3':
            view_expenses()

        elif choice == '4':
            view_income()

        elif choice == '5':
            print("Goodbye!")
            break

        else:
            print("Invalid choice. Please select between 1 and 5.")

# Run the program
if __name__ == '__main__':
    main()

# Close the connection to the database
conn.close()
