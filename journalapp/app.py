from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient
from datetime import datetime, timedelta
import os
import random

app = Flask(__name__)

# Set up MongoDB client
client = MongoClient("mongodb://localhost:27017/")  # Replace with your MongoDB Atlas URI if using Atlas
db = client['journalDB']  # Create or connect to a database called 'journalDB'
collection = db['entries']  # Create or connect to a collection called 'entries'
quotes_collection = db['quotes']  # Create or connect to a collection called 'quotes'

def get_image_list():
    static_folder = os.path.join(app.root_path, 'static')
    images = [file for file in os.listdir(static_folder) if file.endswith(('.jpg', '.jpeg', '.png', '.gif'))]
    return images

@app.route('/')
def home():
    quotes = list(quotes_collection.find())
    random_quote = random.choice(quotes) if quotes else {"text": "No quotes available"}
    images = get_image_list()
    return render_template('index.html', quote=random_quote, images=images)

@app.route('/add', methods=['GET', 'POST'])
def add_entry():
    if request.method == 'POST':
        entry_type = request.form['entry-type']
        thoughts = request.form['thoughts']
        major_emotion = request.form['major-emotion']
        detailed_mood = request.form['detailed-mood']
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        entry = {
            'entry_type': entry_type,
            'thoughts': thoughts,
            'major_emotion': major_emotion,
            'detailed_mood': detailed_mood,
            'timestamp': timestamp
        }

        collection.insert_one(entry)
        return redirect(url_for('home'))

    images = get_image_list()
    return render_template('add_entry.html', images=images)

@app.route('/view')
def view_entries():
    entries = list(collection.find({"entry_type": "journal"}).sort("timestamp", -1))
    images = get_image_list()

    for entry in entries:
        entry_date = datetime.strptime(entry['timestamp'], '%Y-%m-%d %H:%M:%S').date()
        today = datetime.now().date()
        yesterday = today - timedelta(1)
        
        if entry_date == today:
            entry['day'] = "Today"
        elif entry_date == yesterday:
            entry['day'] = "Yesterday"
        else:
            entry['day'] = entry_date.strftime('%B %d, %Y')

        entry['month'] = entry_date.strftime('%B %Y')
        entry['date'] = entry_date.isoformat()

    return render_template('view_entries.html', entries=entries, images=images)

@app.route('/view_dreams')
def view_dreams():
    dreams = list(collection.find({"entry_type": "dream"}).sort("timestamp", -1))
    images = get_image_list()

    for entry in dreams:
        entry_date = datetime.strptime(entry['timestamp'], '%Y-%m-%d %H:%M:%S').date()
        today = datetime.now().date()
        yesterday = today - timedelta(1)
        
        if entry_date == today:
            entry['day'] = "Today"
        elif entry_date == yesterday:
            entry['day'] = "Yesterday"
        else:
            entry['day'] = entry_date.strftime('%B %d, %Y')

        entry['month'] = entry_date.strftime('%B %Y')
        entry['date'] = entry_date.isoformat()

    return render_template('view_dreams.html', entries=dreams, images=images)

if __name__ == "__main__":
    app.run(debug=True)
