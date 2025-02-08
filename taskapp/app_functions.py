import pandas as pd 
import sqlite3
import datetime as dt

def previous_analytics():
    
    # Query the database
    conn = sqlite3.connect('tasks.db')
    c = conn.cursor()

    query = '''
    SELECT "task_name", "category", "duration", 
    "completed_at", "points" FROM completed_tasks 
    ORDER BY completed_at DESC
    '''
    c.execute(query)

    # Fetch tasks and save to dataframe
    tasks = c.fetchall()
    df = pd.DataFrame(tasks, columns=["Task", "Category", "Duration", "Completion Date", "Points"])
    
    # Process dates to remove extra values
    date_strs = df['Completion Date']
    day_dates = []
    for i in date_strs:
        day_date = i.split(' ')[0]
        day_dates.append(day_date)    
    df['Completion Date'] = day_dates

    # Group previous day categories for analysis
    today = dt.datetime.today()
    yesterday = (today - dt.timedelta(days=1))
    day_ofweek = yesterday.strftime("%A")
    yesterday = yesterday.strftime("%Y-%m-%d")

    # Create a filter dataframe
    new_df = df[(df['Completion Date'] == yesterday)].copy()
    cat_grp = new_df.groupby('Category')['Duration'].sum()
    cat_grp.sort_values(ascending=False, inplace=True)

    # Create new dataframe and calculate ratios
    yesterdata = {
        'Category': cat_grp.index,
        'Time Spent': cat_grp.values,
        'Completed Date': yesterday
    }

    yesdf = pd.DataFrame(yesterdata)
    total_duration = int(cat_grp.sum())
    yesdf = pd.DataFrame(yesterdata)
    yesdf['Ratio'] = round(yesdf['Time Spent']/total_duration, 2)
    
    df_values = []
    for row in yesdf.values:
        df_values.append(row)
    
    done_tasks = [f'{done[0]}: {done[-1]}' for done in df_values]
    done_tasks = ', '.join(done_tasks)

    c.execute('INSERT INTO analytics (date_completed, day_of_week, total_duration, tasks_done) VALUES (?, ?, ?, ?)',
            (yesterday, day_ofweek, total_duration, done_tasks))
    
    conn.commit()
    conn.close()


def show_performance ():
    # Query the database
    conn = sqlite3.connect('tasks.db')
    c = conn.cursor()

    query = '''
    SELECT "day_of_week", "date_completed", "total_duration", "tasks_done"
    FROM analytics 
    '''
    c.execute(query)
    
    dones = c.fetchall()
    yester_done = dones[0]
    
    conn.close()
    
    return yester_done
        

# if __name__ == '_main_':
    # previous_analytics()