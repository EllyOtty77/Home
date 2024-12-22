from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
import random
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = 'supersecretkey'

# Task Definitions
DEFAULT_TASKS = [
    {"name": "Nature Walk", "category": "relaxation", "priority": "low"},
    {"name": "Watch a Show", "category": "relaxation", "priority": "low"},
    {"name": "Read a Book", "category": "relaxation", "priority": "low"},
    {"name": "Explore a Complex Idea", "category": "relaxation", "priority": "low"},
]

ART_TASKS = {
    "Music": ['Design', 'theory', 'structure'],
    "Writing": ['descriptive', 'storytelling', 'poetry', 'expository'],
    "Design": ['color', 'thinking', 'theory', 'math'],
    "Art": ['meaning', 'inspiration', 'technique']
}

CAREER_TASKS = {
    "Theory": ['HTTP', 'Statistics'],
    "Language": ['Python', 'Javascript', 'HTML'],
    "Application": ['ML', 'Flask', 'Node'],
    "Domain": ['Research', 'Healthcare', 'Finance', 'Networking'],
    "General": ['Comp Organization', 'Passion', 'Java', 'Dev Ops']
}

HOBBIES = {
    "Personal": ['Speech', 'Philosophy', 'Esoteric', 'Home', 'Cooking'],
    "Interest": ['Cars', 'Film', 'Psychology', 'Health', 'Tech']
}

MONEY_TASKS = ['Forex', 'Business', 'Job search']

# Utility Functions
def pick_random_tasks(task_dict, num_tasks):
    tasks = []
    for category, sub_tasks in task_dict.items():
        selected_task = random.choice(sub_tasks)
        tasks.append({"name": f"{category}: {selected_task}", "category": category.lower(), "priority": "medium"})
    random.shuffle(tasks)
    return tasks[:num_tasks]

def career_pick():
    theory_task = random.choice(CAREER_TASKS["Theory"])
    language_task = "Python" if theory_task == "Statistics" else random.choice(["Javascript", "HTML"])
    application_task = "ML" if theory_task == "Statistics" else random.choice(["Flask", "Node"])
    career_tasks = [
        {"name": f"Theory: {theory_task}", "category": "career", "priority": "high"},
        {"name": f"Language: {language_task}", "category": "career", "priority": "high"},
        {"name": f"Application: {application_task}", "category": "career", "priority": "high"},
        {"name": f"Domain: {random.choice(CAREER_TASKS['Domain'])}", "category": "career", "priority": "high"},
        {"name": f"General: {random.choice(CAREER_TASKS['General'])}", "category": "career", "priority": "high"},
    ]
    return career_tasks

def initialize_default_tasks():
    default_tasks = DEFAULT_TASKS + pick_random_tasks(ART_TASKS, 3) + career_pick()
    random.shuffle(MONEY_TASKS)
    default_tasks.append({"name": random.choice(MONEY_TASKS), "category": "money", "priority": "high"})
    default_tasks += [
        {"name": random.choice(HOBBIES["Personal"]), "category": "hobby", "priority": "medium"},
        {"name": random.choice(HOBBIES["Interest"]), "category": "hobby", "priority": "medium"}
    ]

    random.shuffle(default_tasks)
    
    week_day = datetime.now().strftime("%A")
    
    if week_day in ['Monday,' 'Tuesday', 'Wednesday']:
        default_tasks = default_tasks
    elif week_day == 'Thursday':
    	default_tasks = default_tasks[:8]
    elif week_day == 'Friday':
    	default_tasks = default_tasks[:7]
    elif week_day == 'Saturday':
        random.shuffle(DEFAULT_TASKS)
        default_tasks = DEFAULT_TASKS[:-2] + pick_random_tasks(ART_TASKS, 1)
        default_tasks += [
        {"name": random.choice(HOBBIES["Personal"]), "category": "hobby", "priority": "medium"},
        {"name": random.choice(HOBBIES["Interest"]), "category": "hobby", "priority": "medium"},
	{"name": random.choice(HOBBIES["Interest"]), "category": "hobby", "priority": "medium"}
    ]
    elif week_day == 'Sunday':
    	default_tasks = DEFAULT_TASKS

    with sqlite3.connect('tasks.db') as conn:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM tasks')
        for task in default_tasks:
            duration = random.choice([15, 25, 30, 40, 60])
            points = calculate_points(task['priority'])
            cursor.execute('INSERT INTO tasks (name, category, duration, priority, points) VALUES (?, ?, ?, ?, ?)',
                           (task['name'], task['category'], duration, task['priority'], points))
        conn.commit()

def calculate_points(priority):
    return {"high": 10, "medium": 5, "low": 2}.get(priority, 2)

# Flask Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/add_task', methods=['POST'])
def add_task():
    name = request.form['name']
    category = request.form['category']
    priority = request.form['priority']
    points = calculate_points(priority)
    duration = random.choice([20, 30, 40, 60])
    with sqlite3.connect('tasks.db') as conn:
        cursor = conn.cursor()
        cursor.execute('INSERT INTO tasks (name, category, duration, priority, points) VALUES (?, ?, ?, ?, ?)',
                       (name, category, duration, priority, points))
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
            completed_at = datetime.now() + timedelta(minutes=task[3])
            cursor.execute('INSERT INTO completed_tasks (task_id, task_name, category, duration, completed_at, points) VALUES (?, ?, ?, ?, ?, ?)',
                           (task[0], task[1], task[2], task[3], completed_at, task[5]))
            cursor.execute('DELETE FROM tasks WHERE id = ?', (task[0],))
            conn.commit()
    return render_template('task.html', task=task)

@app.route('/view_tasks')
def view_tasks():
    today = datetime.now().strftime('%Y-%m-%d')
    with sqlite3.connect('tasks.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM tasks ORDER BY category ASC')
        remaining_tasks = cursor.fetchall()
        cursor.execute('SELECT task_name, category, duration, completed_at, points FROM completed_tasks WHERE DATE(completed_at) = ?', (today,))
        completed_tasks = cursor.fetchall()
    return render_template('view_tasks.html', remaining_tasks=remaining_tasks, completed_tasks=completed_tasks)

@app.route('/init_tasks')
def init_tasks():
    initialize_default_tasks()
    return redirect(url_for('view_tasks'))

@app.route('/progress')
def progress():
    with sqlite3.connect('tasks.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT category, SUM(duration) FROM completed_tasks GROUP BY category')
        data = cursor.fetchall()
        cursor.execute('SELECT SUM(points) FROM completed_tasks')
        total_points = cursor.fetchone()[0]
    categories = [row[0] for row in data]
    durations = [row[1] for row in data]
    return render_template('progress.html', categories=categories, durations=durations, total_points=total_points)

if __name__ == '__main__':
    app.run(debug=True)
