from pymongo import MongoClient

def add_quotes():
    # Set up MongoDB client
    client = MongoClient("mongodb://localhost:27017/")  # Replace with your MongoDB Atlas URI if using Atlas
    db = client['journalDB']  # Create or connect to a database called 'journalDB'
    quotes_collection = db['quotes']  # Create or connect to a collection called 'quotes'

    quotes = []
    while True:
        text = input("Enter the quote text (or type 'done' to finish): ")
        if text.lower() == 'done':
            break
        quote = {"text": text}
        quotes.append(quote)

    if quotes:
        # Insert quotes into the MongoDB collection
        quotes_collection.insert_many(quotes)
        print("Quotes added successfully!")
    else:
        print("No quotes were added.")

if __name__ == "__main__":
    add_quotes()
