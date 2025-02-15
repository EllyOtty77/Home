import pandas as pd 
import sqlite3
import datetime as dt

db_path = 'C:/Users/user/Desktop/Repositories/Home/taskapp/tasks.db'
def weekly_analytics():
    # Connect to the database
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    # Query completed tasks
    query = '''
    SELECT "task_name", "category", "duration", "completed_at", "points" FROM completed_tasks 
    ORDER BY completed_at DESC
    '''
    c.execute(query)
    tasks = c.fetchall()
    df = pd.DataFrame(tasks, columns=["Task", "Category", "Duration", "Completion Date", "Points"])
    
    # Convert 'Completion Date' to datetime and extract date
    df['Completion Date'] = pd.to_datetime(df['Completion Date']).dt.date
    
    # Define date range (Monday to Saturday)
    today = dt.date.today()
    last_monday = today - dt.timedelta(days=today.weekday())
    last_saturday = last_monday + dt.timedelta(days=5)
    
    # Filter tasks within Monday-Saturday range
    week_df = df[(df['Completion Date'] >= last_monday) & (df['Completion Date'] <= last_saturday)]
    
    if week_df.empty:
        print("No completed tasks found for the current week.")
        return
    
    # Group by category and calculate time spent per category
    cat_grp = week_df.groupby('Category')['Duration'].sum()
    cat_grp.sort_values(ascending=False, inplace=True)
    
    # Create dataframe for weekly summary
    week_data = {
        'Category': cat_grp.index,
        'Time Spent': cat_grp.values,
        'Completed Date': f'{last_monday} to {last_saturday}'
    }
    
    week_df_summary = pd.DataFrame(week_data)
    total_duration = int(cat_grp.sum())
    week_df_summary['Ratio'] = round(week_df_summary['Time Spent'] / total_duration, 2)
    
    # Prepare data for insertion
    df_values = [f'{done[0]}: {done[-1]}' for done in week_df_summary.values]
    done_tasks = ', '.join(df_values)
    
    # Insert weekly analytics into the database
    c.execute('''
        INSERT INTO analytics (date_completed, day_of_week, total_duration, tasks_done) 
        VALUES (?, ?, ?, ?)''',
        (f'{last_monday} to {last_saturday}', 'Weekly Summary', total_duration, done_tasks))
    
    conn.commit()
    conn.close()

def show_weekly_performance():
    # Connect to the database
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    # Retrieve weekly summary
    query = '''
    SELECT date_completed, day_of_week, total_duration, tasks_done FROM analytics 
    WHERE day_of_week = "Weekly Summary" 
    ORDER BY date_completed DESC LIMIT 1
    '''
    c.execute(query)
    weekly_done = c.fetchone()
    
    conn.close()
    
    return weekly_done
print(show_weekly_performance())