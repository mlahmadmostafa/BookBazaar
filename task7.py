from flask import Flask, request, jsonify
import sqlite3
import threading
from contextlib import closing
import os 
# Connect to the SQLite database
conn = sqlite3.connect('bookbazaar.db')
cursor = conn.cursor()

#cursor.execute("DROP TABLE IF EXISTS Users;")
#cursor.execute("DROP TABLE IF EXISTS Authors;")
#cursor.execute("DROP TABLE IF EXISTS Books;")


# Create the Users table
cursor.execute('''
CREATE TABLE IF NOT EXISTS Users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    email TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL
);
''')

# Create the Authors table
cursor.execute('''
CREATE TABLE IF NOT EXISTS Authors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    country TEXT
);
''')

# Create the Books table
cursor.execute('''
CREATE TABLE IF NOT EXISTS Books (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    author_id INTEGER NOT NULL,
    genre TEXT,
    published_year INTEGER,
    FOREIGN KEY (author_id) REFERENCES Authors(id)
);
''')

# Commit the changes
conn.commit()
# Close the connection
cursor.close()
conn.close()

# Connect to the database
conn = sqlite3.connect('bookbazaar.db')
cursor = conn.cursor()

try:
    # Insert sample data into Users table
    cursor.execute('''
    INSERT INTO Users (username, email, password_hash)
    VALUES 
    ('user1', 'user1@example.com', 'hash1'),
    ('user2', 'user2@example.com', 'hash2');
    ''')
    print("Sample Users data inserted successfully!")
    # Insert sample data into Authors table
    cursor.execute('''
    INSERT INTO Authors (name, country)
    VALUES 
    ('Yahya Al-Sinwar', 'Gaza'),
    ('J.K. Rowling', 'United Kingdom'),
    ('George Orwell', 'United Kingdom'),
    ('Agatha Christie', 'United Kingdom');
    ''')
    print("Sample Authors data inserted successfully!")

    # Insert sample data into Books table
    cursor.execute('''
    INSERT INTO Books (title, author_id, genre, published_year)
    VALUES 
    ('The Thorn and the Carnation', 1, 'War', 2025),
    ('Harry Potter and the Philosopher''s Stone', 2, 'Fantasy', 1997),
    ('1984', 3, 'Dystopian', 1949),
    ('Murder on the Orient Express', 4, 'Mystery', 1934);
    ''')
    print("Sample Books data inserted successfully!")

    # Commit the changes
    conn.commit()

    # Close the connection
    cursor.close()
    conn.close()
    
except sqlite3.Error as e:
    print(f"An error occurred: {e}")
    

def connect_db(db_file):
    """Connect to the SQLite database and return the connection object."""
    try:
        # Check if the database file exists
        if not os.path.exists(db_file):
            raise FileNotFoundError(f"The database file '{db_file}' does not exist.")
        
        # Connect to the database
        conn = sqlite3.connect(db_file)
        print(f"Connected to the database '{db_file}' successfully!")
        return conn
    except sqlite3.Error as e:
        print(f"An error occurred while connecting to the database: {e}")
        return None
    except FileNotFoundError as e:
        print(e)
        return None

# Define the database file path
db_file = "bookbazaar.db"

# Establish a connection to the database
try:
    conn = sqlite3.connect(db_file)
    print(f"Connected to the database '{db_file}' successfully!")
except sqlite3.Error as e:
    print(f"An error occurred while connecting to the database: {e}")

conn = connect_db(db_file)

def insert_book(title, author_id, genre, published_year):
    """Insert a new book into the Books table."""
    try:
        cursor = conn.cursor()
        cursor.execute('''
        INSERT INTO Books (title, author_id, genre, published_year)
        VALUES (?, ?, ?, ?)
        ''', (title, author_id, genre, published_year))
        conn.commit()
        print("Book inserted successfully!")
    except sqlite3.Error as e:
        print(f"An error occurred while inserting the book: {e}")

def get_book(book_id):
    """Retrieve a book by its ID."""
    try:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM Books WHERE id = ?', (book_id,))
        book = cursor.fetchone()
        if book:
            return book
        else:
            print(f"No book found with ID {book_id}.")
            return None
    except sqlite3.Error as e:
        print(f"An error occurred while retrieving the book: {e}")
        return None

def get_all_books():
    """Retrieve all books from the Books table."""
    try:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM Books')
        books = cursor.fetchall()
        return books
    except sqlite3.Error as e:
        print(f"An error occurred while retrieving books: {e}")
        return None
    
def update_book(book_id, title=None, genre=None, published_year=None):
    """Update a book's information."""
    try:
        cursor = conn.cursor()
        
        # Check if the book exists
        cursor.execute('SELECT id FROM Books WHERE id = ?', (book_id,))
        if not cursor.fetchone():
            print(f"No book found with ID {book_id}.")
            return
        
        # Update the book's information
        if title:
            cursor.execute('UPDATE Books SET title = ? WHERE id = ?', (title, book_id))
        if genre:
            cursor.execute('UPDATE Books SET genre = ? WHERE id = ?', (genre, book_id))
        if published_year:
            cursor.execute('UPDATE Books SET published_year = ? WHERE id = ?', (published_year, book_id))
        
        # Check if any rows were updated
        if cursor.rowcount > 0:
            conn.commit()
            print("Book updated successfully!")
        else:
            print("No changes made to the book.")
    except sqlite3.Error as e:
        print(f"An error occurred while updating the book: {e}")

def delete_book(book_id):
    """Delete a book by its ID."""
    try:
        cursor = conn.cursor()
        
        # Check if the book exists
        cursor.execute('SELECT id FROM Books WHERE id = ?', (book_id,))
        if not cursor.fetchone():
            print(f"No book found with ID {book_id}.")
            return
        
        # Delete the book
        cursor.execute('DELETE FROM Books WHERE id = ?', (book_id,))
        
        # Check if any rows were deleted
        if cursor.rowcount > 0:
            conn.commit()
            print("Book deleted successfully!")
        else:
            print("No book was deleted.")
    except sqlite3.Error as e:
        print(f"An error occurred while deleting the book: {e}")



# Initialize Flask app
app = Flask(__name__)

# Function to get a database connection
def get_db_connection(db_file):
    conn = sqlite3.connect(db_file)
    conn.row_factory = sqlite3.Row  # Return rows as dictionaries
    return conn

# Home route
@app.route('/')
def home():
    return "Hello, Flask! This is the home page."

# Route to get all books
@app.route('/books', methods=['GET'])
def get_books():
    """Retrieve all books from the Books table."""
    conn = get_db_connection("bookbazaar.db")
    cursor = conn.cursor()
    try:
        cursor.execute('SELECT * FROM Books')
        books = cursor.fetchall()
        return jsonify([dict(book) for book in books]), 200
    except sqlite3.Error as e:
        return jsonify({"error": f"An error occurred while retrieving books: {e}"}), 500
    finally:
        conn.close()

# Route to add a new book
@app.route('/books', methods=['POST'])
def add_book():
    """Add a new book to the Books table."""
    conn = get_db_connection("bookbazaar.db")
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500

    data = request.get_json()
    if not data or not all(key in data for key in ['title', 'author_id', 'genre', 'published_year']):
        return jsonify({"error": "Invalid input: Ensure 'title', 'author_id', 'genre', and 'published_year' are provided"}), 400

    cursor = conn.cursor()
    try:
        cursor.execute('''
        INSERT INTO Books (title, author_id, genre, published_year)
        VALUES (?, ?, ?, ?)
        ''', (data['title'], data['author_id'], data['genre'], data['published_year']))
        conn.commit()
        return jsonify({"message": "Book added successfully!"}), 201
    except sqlite3.Error as e:
        return jsonify({"error": f"An error occurred while adding the book: {e}"}), 500
    finally:
        conn.close()

# Route to update a book
@app.route('/books/<int:book_id>', methods=['PUT'])
def update_book(book_id):
    """Update a book's information."""
    conn = get_db_connection("bookbazaar.db")
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500

    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid input: No data provided"}), 400

    cursor = conn.cursor()
    try:
        # Check if the book exists
        cursor.execute('SELECT id FROM Books WHERE id = ?', (book_id,))
        if not cursor.fetchone():
            return jsonify({"error": f"No book found with ID {book_id}"}), 404

        # Update the book's information
        update_fields = []
        update_values = []
        for key in ['title', 'genre', 'published_year']:
            if key in data:
                update_fields.append(f"{key} = ?")
                update_values.append(data[key])

        if not update_fields:
            return jsonify({"error": "No valid fields provided for update"}), 400

        update_values.append(book_id)
        query = f"UPDATE Books SET {', '.join(update_fields)} WHERE id = ?"
        cursor.execute(query, update_values)
        conn.commit()

        return jsonify({"message": "Book updated successfully!"}), 200
    except sqlite3.Error as e:
        return jsonify({"error": f"An error occurred while updating the book: {e}"}), 500
    finally:
        conn.close()

# Route to delete a book
@app.route('/books/<int:book_id>', methods=['DELETE'])
def delete_book(book_id):
    """Delete a book by its ID."""
    conn = get_db_connection("bookbazaar.db")
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500

    cursor = conn.cursor()
    try:
        # Check if the book exists
        cursor.execute('SELECT id FROM Books WHERE id = ?', (book_id,))
        if not cursor.fetchone():
            return jsonify({"error": f"No book found with ID {book_id}"}), 404

        # Delete the book
        cursor.execute('DELETE FROM Books WHERE id = ?', (book_id,))
        conn.commit()
        return jsonify({"message": "Book deleted successfully!"}), 200
    except sqlite3.Error as e:
        return jsonify({"error": f"An error occurred while deleting the book: {e}"}), 500
    finally:
        conn.close()

# Function to run the Flask app in a separate thread
def run_flask():
    print("Starting Flask server...")
    app.run(debug=True, port=5001, use_reloader=False)

# Start the Flask app in a separate thread
thread = threading.Thread(target=run_flask)
thread.start()

print("Flask server is running on http://127.0.0.1:5001")