-- Initialize Database: tasks.db

-- Drop existing tables if they exist (for development purposes)
DROP TABLE IF EXISTS tasks;
DROP TABLE IF EXISTS completed_tasks;
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS analytics;


-- Create tasks table
CREATE TABLE tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    category TEXT NOT NULL,
    duration INTEGER NOT NULL
);

-- Create completed_tasks table with task name and adjusted completion time
CREATE TABLE completed_tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id INTEGER NOT NULL,
    task_name TEXT NOT NULL,
    category TEXT NOT NULL,
    duration INTEGER NOT NULL,
    completed_at TIMESTAMP NOT NULL,
    FOREIGN KEY (task_id) REFERENCES tasks(id)
);

-- Create table for summary analytics
CREATE TABLE analytics (
    date_completed TEXT NOT NULL PRIMARY KEY,
    day_of_week TEXT NOT NULL,
    total_duration INTEGER NOT NULL,
    tasks_done TEXT NOT NULL
);
