-- Initialize Database: tasks.db

-- Drop existing tables if they exist (for development purposes)
DROP TABLE IF EXISTS tasks;
DROP TABLE IF EXISTS completed_tasks;
DROP TABLE IF EXISTS users;

-- Create users table
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL
);

-- Create tasks table
CREATE TABLE tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    category TEXT NOT NULL,
    duration INTEGER NOT NULL,
    priority TEXT NOT NULL,
    points INTEGER NOT NULL DEFAULT 0
);

-- Create completed_tasks table with task name and adjusted completion time
CREATE TABLE completed_tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id INTEGER NOT NULL,
    task_name TEXT NOT NULL,
    category TEXT NOT NULL,
    duration INTEGER NOT NULL,
    completed_at TIMESTAMP NOT NULL,
    points INTEGER NOT NULL,
    FOREIGN KEY (task_id) REFERENCES tasks(id)
);
