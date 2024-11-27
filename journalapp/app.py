from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient
from datetime import datetime

app = Flask(__name__)

# Set up MongoDB client
client = MongoClient("mongodb://localhost:27017/")  # Replace with your MongoDB Atlas URI if using Atlas
db = client['journalDB']  # Create or connect to a database called 'journalDB'
collection = db['entries']  # Create or connect to a collection called 'entries'

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/add', methods=['GET', 'POST'])
def add_entry():
    if request.method == 'POST':
        thoughts = request.form['thoughts']
        mood = request.form['mood']
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        entry = {
            'thoughts': thoughts,
            'mood': mood,
            'timestamp': timestamp
        }

        # Insert the entry into the MongoDB collection
        collection.insert_one(entry)
        return redirect(url_for('home'))

    return render_template('add_entry.html')

@app.route('/view')
def view_entries():
    # Retrieve all journal entries
    entries = collection.find().sort("timestamp", -1)
    return render_template('view_entries.html', entries=entries)

if __name__ == "__main__":
    app.run(debug=True)
