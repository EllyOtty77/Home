from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
import random
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = 'supersecretkey'

# Task Definitions
DEFAULT_TASKS = [
    # {"name": "Nature Walk", "category": "Relaxation", "priority": "low"},
    # {"name": "Watch Something", "category": "Relaxation", "priority": "low"},
    # {"name": "Read a Book", "category": "Relaxation", "priority": "low"},
    {"name": "Explore a Complex Idea", "category": "Relaxation", "priority": "low"},
]

ART_TASKS = {
    "Music": ['Design', 'Theory', 'Structure'],
    "Writing": ['Poetry', 'Article', 'Descriptive'],
    "Design": ['Graphic', 'Thinking'],
    "Art": ['Meaning', 'Inspiration']
}

CAREER_TASKS = {
    "Theory": ['The Internet', 'Statistics'],
    "Language": ['Python', 'Javascript', 'Java'],
    "Application": ['ML', 'Frontend', 'Backend'],
    "Domain": ['DevOps', 'Healthcare', 'Finance'],
    "General": ['Comp Organization', 'Database']
}

HOBBIES = {
    "Personal": ['Speech', 'Philosophy', 'Esoteric', 'Health',  'Home & Food'],
    "Interest": ['Cars', 'Film', 'Psychology', 'Tech', 'Space']
}

MONEY_TASKS = ['Forex', 'Job search']

# Utility Functions
def pick_random_tasks(task_dict, num_tasks):
    tasks = [{"name": f"{category}: {random.choice(sub_tasks)}", "category": category.capitalize(), "priority": "medium"}
             for category, sub_tasks in task_dict.items()]
    random.shuffle(tasks)
    return tasks[:num_tasks]

def career_pick():
    theory_task = random.choice(CAREER_TASKS["Theory"])
    general_task = random.choice(CAREER_TASKS["General"])
    language_task = "Python" if theory_task == "Statistics" else random.choice(["Javascript", "Java"])
    if theory_task == "Statistics":
        application_task = "ML" 
    elif theory_task == "The Internet":
       application_task = random.choice(['Frontend', 'Backend'])
       if application_task == 'Backend':
            application_task = random.choice(["Node", "Flask"])
       else:
           application_task = application_task 
    if general_task == 'Database':
        general_task = random.choice(["MySQL", "MongoDB", "SQLite"])
    else:
        general_task = general_task

    career_picks =  [
        {"name": f"Theory: {theory_task}", "category": "Career", "priority": "high"},
        {"name": f"Language: {language_task}", "category": "Career", "priority": "high"},
        {"name": f"Application: {application_task}", "category": "Career", "priority": "high"},
        {"name": f"Domain: {random.choice(CAREER_TASKS['Domain'])}", "category": "Career", "priority": "high"},
        {"name": f"General: {general_task}", "category": "Career", "priority": "high"}
    ]
    
    random.shuffle(career_picks)
    return career_picks[:-2]

def calculate_points(priority):
    return {"high": 10, "medium": 5, "low": 2}.get(priority, 2)

def initialize_default_tasks():
    tasks = DEFAULT_TASKS + pick_random_tasks(ART_TASKS, 2) + career_pick() + [
        {"name": random.choice(MONEY_TASKS), "category": "Money", "priority": "high"},
        {"name": random.choice(HOBBIES["Personal"]), "category": "Hobby", "priority": "medium"},
        {"name": random.choice(HOBBIES["Interest"]), "category": "Hobby", "priority": "medium"}
    ]

    week_day = datetime.now().strftime("%A")
    
    if week_day == 'Thursday':
        tasks = tasks[:6]
    elif week_day == 'Friday':
        tasks = tasks[:5]
        if not any(task["name"] == "Nature Walk" for task in tasks):
            tasks.append({"name": "Nature Walk", "category": "Relaxation", "priority": "low"})
        if len(tasks) > 5:
            tasks = random.sample(tasks, 5)
    elif week_day == 'Saturday':
        tasks = DEFAULT_TASKS + pick_random_tasks(ART_TASKS, 1) + [
            {"name": random.choice(HOBBIES["Personal"]), "category": "Hobby", "priority": "medium"},
            {"name": random.choice(HOBBIES["Interest"]), "category": "Hobby", "priority": "medium"},
            {"name": random.choice(HOBBIES["Interest"]), "category": "Hobby", "priority": "medium"}
        ]
    elif week_day == 'Sunday':
        tasks = DEFAULT_TASKS

    with sqlite3.connect('tasks.db') as conn:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM tasks')
        for task in tasks:
            points = calculate_points(task['priority'])
            cursor.execute('INSERT INTO tasks (name, category, duration, priority, points) VALUES (?, ?, ?, ?, ?)',
                           (task['name'], task['category'], 0, task['priority'], points))
        conn.commit()

# Flask Routes
@app.route('/')
def index():
    with sqlite3.connect('tasks.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT id, name, category, priority FROM tasks ORDER BY category ASC')
        remaining_tasks = cursor.fetchall()
        cursor.execute('SELECT COUNT(*) FROM tasks')
        tasks_remaining = cursor.fetchone()[0]
        today = datetime.now().strftime('%Y-%m-%d')
        cursor.execute('SELECT COUNT(*) FROM completed_tasks WHERE DATE(completed_at) = ?', (today,))
        tasks_completed = cursor.fetchone()[0]

    if tasks_remaining + tasks_completed > 0:
        completion_percentage = int((tasks_completed / (tasks_remaining + tasks_completed)) * 100)
    else:
        completion_percentage = 0

    motivational_message = f"You've completed {completion_percentage}% of your tasks today! Keep going!"

    # Fetch current task if any
    current_task = None
    cursor.execute('SELECT * FROM completed_tasks ORDER BY id DESC LIMIT 1')
    current_task = cursor.fetchone()

    return render_template('index.html', current_task=current_task, tasks_remaining=tasks_remaining, motivational_message=motivational_message, completion_percentage=completion_percentage)

@app.route('/add_task', methods=['POST'])
def add_task():
    name = request.form['name']
    category = request.form['category']
    priority = request.form['priority']
    points = calculate_points(priority)
    duration = 0
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
            duration = random.choice([15, 25, 30, 40, 50])
            completed_at = datetime.now() + timedelta(minutes=duration)
            cursor.execute('INSERT INTO completed_tasks (task_id, task_name, category, duration, completed_at, points) VALUES (?, ?, ?, ?, ?, ?)',
                           (task[0], task[1], task[2], duration, completed_at, task[5]))
            cursor.execute('DELETE FROM tasks WHERE id = ?', (task[0],))
            conn.commit()

        # Fetch the current task
        cursor.execute('SELECT * FROM completed_tasks ORDER BY id DESC LIMIT 1')
        current_task = cursor.fetchone()
    
    return render_template('task.html', task=task, duration=duration, current_task=current_task)

@app.route('/view_tasks')
def view_tasks():
    today = datetime.now().strftime('%Y-%m-%d')
    with sqlite3.connect('tasks.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT id, name, category, priority, points FROM tasks ORDER BY category ASC')
        remaining_tasks = cursor.fetchall()
    cursor.execute('SELECT task_name, category, duration, completed_at, points FROM completed_tasks WHERE DATE(completed_at) = ?', (today,)) 
    completed_tasks = cursor.fetchall() 
    return render_template('view_tasks.html', remaining_tasks=remaining_tasks,   completed_tasks=completed_tasks)

@app.route('/init_tasks')
def init_tasks():
    initialize_default_tasks()
    return redirect(url_for('view_tasks'))

if __name__ == '__main__':
    app.run(debug=True)
