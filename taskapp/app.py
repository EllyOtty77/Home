from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
import random
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = 'supersecretkey'

# Define default tasks
def_tasks = [
    {"name": "Nature Walk", "category": "relaxation", "priority": "low"},
    {"name": "Watch a Show", "category": "relaxation", "priority": "low"},
    {"name": "Listen to Music", "category": "relaxation", "priority": "low"},
    {"name": "Play a Game", "category": "relaxation", "priority": "low"},
    {"name": "Read a Book", "category": "relaxation", "priority": "low"},
    {"name": "Explore a Complex Idea", "category": "relaxation", "priority": "low"},
]

Art = {"Music":['Design', 'theory', 'structure'],
       "Writing": ['descriptive', 'storytelling', 'poetry', 'expository'],
       "Design":['color', 'thinking', 'form'],
       "Art": ['meaning', 'inspiration', 'technique']}

def art_pick():
    art_tasks = []
    for key in Art:
        minis = Art[key]
        random.shuffle(minis)
        mini = random.choice(minis)
        task_name = f"{key}: {mini}"
        task_dict= {}
        task_dict["name"] = task_name
        task_dict["category"] = 'art'
        task_dict["priority"] = 'medium'
        
        art_tasks.append(task_dict)
    return art_tasks

    
def initialize_default_tasks():
    default_tasks = []
    default_tasks.extend(def_tasks)
    default_tasks.extend(art_pick())
    conn = sqlite3.connect('tasks.db')
    cursor = conn.cursor()
    # Clear existing tasks
    cursor.execute('DELETE FROM tasks')
    # Add default tasks
    for task in default_tasks:
        duration = random.choice([15, 25, 30, 40, 60])
        points = calculate_points(task['priority'])
        cursor.execute('INSERT INTO tasks (name, category, duration, priority, points) VALUES (?, ?, ?, ?, ?)',
                       (task['name'], task['category'], duration, task['priority'], points))
    conn.commit()
    conn.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/add_task', methods=['POST'])
def add_task():
    name = request.form['name']
    category = request.form['category']
    priority = request.form['priority']
    points = calculate_points(priority)
    conn = sqlite3.connect('tasks.db')
    cursor = conn.cursor()
    duration = random.choice([40, 60, 100] if category == 'project' else [20, 30, 40, 60])
    cursor.execute('INSERT INTO tasks (name, category, duration, priority, points) VALUES (?, ?, ?, ?, ?)',
                   (name, category, duration, priority, points))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

def calculate_points(priority):
    if priority == 'high':
        return 10
    elif priority == 'medium':
        return 5
    return 2

@app.route('/pick_task')
def pick_task():
    conn = sqlite3.connect('tasks.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM tasks')
    tasks = cursor.fetchall()
    if len(tasks) > 0:
        random.shuffle(tasks)
        task = random.choice(tasks)
        if task:
            completed_at = datetime.now() + timedelta(minutes=task[3])
            cursor.execute('INSERT INTO completed_tasks (task_id, task_name, category, duration, completed_at, points) VALUES (?, ?, ?, ?, ?, ?)',
                           (task[0], task[1], task[2], task[3], completed_at, task[5]))
            cursor.execute('DELETE FROM tasks WHERE id = ?', (task[0],))
            conn.commit()
    conn.close()
    return render_template('task.html', task=task)

@app.route('/view_tasks')
def view_tasks():
    conn = sqlite3.connect('tasks.db')
    cursor = conn.cursor()
    # Fetch remaining tasks
    cursor.execute('SELECT * FROM tasks ORDER BY priority DESC')
    remaining_tasks = cursor.fetchall()
    # Fetch completed tasks
    cursor.execute('SELECT task_name, category, duration, completed_at, points FROM completed_tasks')
    completed_tasks = cursor.fetchall()
    conn.close()
    return render_template('view_tasks.html', remaining_tasks=remaining_tasks, completed_tasks=completed_tasks)

@app.route('/init_tasks')
def init_tasks():
    initialize_default_tasks()
    return redirect(url_for('view_tasks'))

@app.route('/progress')
def progress():
    conn = sqlite3.connect('tasks.db')
    cursor = conn.cursor()
    cursor.execute('SELECT category, SUM(duration) FROM completed_tasks GROUP BY category')
    data = cursor.fetchall()
    cursor.execute('SELECT SUM(points) FROM completed_tasks')
    total_points = cursor.fetchone()[0]
    conn.close()
    categories = [row[0] for row in data]
    durations = [row[1] for row in data]
    return render_template('progress.html', categories=categories, durations=durations, total_points=total_points)

if __name__ == '__main__':
    app.run(debug=True)
