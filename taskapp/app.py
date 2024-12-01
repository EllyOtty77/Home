from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
import random
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = 'supersecretkey'

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
    duration = random.choice([20, 30, 40, 60, 100] if category == 'project' else [20, 30, 40, 60])
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
    cursor.execute('SELECT * FROM tasks ORDER BY priority DESC, RANDOM() LIMIT 1')
    task = cursor.fetchone()
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
