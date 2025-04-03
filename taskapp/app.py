from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import random
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = 'supersecretkey'

# Task selection
def select_tasks(task_list, label, sample_size=None):
    selected = random.sample(task_list, sample_size) if sample_size else [random.choice(task_list)]
    tasks = []
    for item in selected:
        for key, values in item.items():
            tasks.append(f'{key} - {random.choice(values)}:{label}')
    return tasks

# Career tasks
career_tasks = {
    "Developer": [
        {"Web": ['React', 'Flask', 'The Internet']},
        {"Data": ['Data Analysis', 'SQL', 'DB Design']},
        {"Automation": ['Java', 'Python', 'Terminal']},
        {"Computing": ['Git', 'Algorithms', 'Software Engineering']}
    ],
    "Medical": [
        {"Physiology": ['Medical Physiology']},
        {"Chemistry": ['Biochemistry', 'Pharmacology']}
    ],
    "Money": [
        {"Trading": ['MT5', 'Knowledge']},
        {"Business": ['Economics', 'Entrepreneurship']}
    ]
}

# Art tasks
art_tasks = {
    "Music": ['Theory', 'Sound Design', 'DJ'], 
    "Writing": ['Poetry', 'Descriptive Writing'],
    "Design": ['Design Thinking', 'Graphic Design']
}

# Daily task list
def generate_task_list(day, tasks):
    sizes = {'Monday': 8, 'Tuesday': 8, 'Wednesday': 8, 'Thursday': 7, 'Friday': 6, 'Saturday': 5}
    sample_size = sizes.get(day, 0)
    return random.sample(tasks, min(sample_size, len(tasks)))     


def initialize_default_tasks():
    career_stuff = []
    career_stuff += select_tasks(career_tasks['Developer'], "Career", sample_size=4)
    career_stuff += select_tasks(career_tasks['Medical'], "Career")  # one random item from Medical
    career_stuff += select_tasks(career_tasks['Money'], "Career", sample_size=2)

    art_stuff = [f'{key} - {random.choice(values)}:Art' for key, values in art_tasks.items()]
    random.shuffle(art_stuff)
    art_stuff = random.sample(art_stuff, 2)

    all_tasks = career_stuff + art_stuff

    current_day = datetime.today().strftime("%A")
    daily_tasks = generate_task_list(current_day, all_tasks)
    with sqlite3.connect('tasks.db') as conn:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM tasks')
        for t in daily_tasks:
            task = t.split(':')[0]
            task_category = t.split(':')[1].strip()
            cursor.execute('INSERT INTO tasks (name, duration, category) VALUES (?, ?, ?)', (task, 0, task_category))
        conn.commit()

@app.route('/')
def index():
    with sqlite3.connect('tasks.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT id, name FROM tasks')
        remaining_tasks = cursor.fetchall()
        cursor.execute('SELECT COUNT(*) FROM tasks')
        tasks_remaining = cursor.fetchone()[0]
        today = datetime.now().strftime('%Y-%m-%d')
        cursor.execute('SELECT COUNT(*) FROM completed_tasks WHERE DATE(completed_at) = ?', (today,))
        tasks_completed = cursor.fetchone()[0]
    
    completion_percentage = (tasks_completed / (tasks_remaining + tasks_completed) * 100) if tasks_remaining + tasks_completed > 0 else 0
    completion_percentage = int(round(completion_percentage, 0))
    motivational_message = f"You've completed {completion_percentage}% of your tasks today! Keep going!"
     
    # Fetch current task if any
    current_task = None
    cursor.execute('SELECT * FROM completed_tasks ORDER BY id DESC LIMIT 1')
    current_task = cursor.fetchone()

    return render_template('index.html', current_task=current_task, tasks_remaining=tasks_remaining, motivational_message=motivational_message, completion_percentage=completion_percentage)


@app.route('/add_task', methods=['POST'])
def add_task():
    name = request.form['name']
    with sqlite3.connect('tasks.db') as conn:
        cursor = conn.cursor()
        cursor.execute('INSERT INTO tasks (name, duration) VALUES (?, ?)', (name, 0))
        conn.commit()
    return redirect(url_for('index'))

@app.route('/pick_task')
def pick_task():
    with sqlite3.connect('tasks.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM tasks')
        tasks = cursor.fetchall()
        if tasks:
            task = random.choice(tasks)
            duration = random.choice([15, 25, 30, 40, 50])
            completed_at = datetime.now() + timedelta(minutes=duration)
            completed_at = completed_at.strftime("%Y-%m-%d %H:%M")
            cursor.execute('INSERT INTO completed_tasks (task_id, task_name, category, duration, completed_at) VALUES (?, ?, ?, ?, ?)',
                           (task[0], task[1], task[2], duration, completed_at))
            cursor.execute('DELETE FROM tasks WHERE id = ?', (task[0],))
            conn.commit()
    
    cursor.execute('SELECT * FROM completed_tasks ORDER BY id DESC LIMIT 1')
    current_task = cursor.fetchone()
    return render_template('task.html', task=task, duration=duration, current_task=current_task)


@app.route('/view_tasks')
def view_tasks():
    today = datetime.now().strftime('%Y-%m-%d')
    with sqlite3.connect('tasks.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT id, name, category FROM tasks')
        remaining_tasks = cursor.fetchall()
        cursor.execute('SELECT task_name, category, duration, completed_at FROM completed_tasks WHERE DATE(completed_at) = ?', (today,)) 
        completed_tasks = cursor.fetchall() 
    return render_template('view_tasks.html', remaining_tasks=remaining_tasks, completed_tasks=completed_tasks)

@app.route('/init_tasks')
def init_tasks():
    initialize_default_tasks()
    return redirect(url_for('view_tasks'))

if __name__ == '__main__':
    app.run(debug=True)
