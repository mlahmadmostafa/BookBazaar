import os
import sqlite3
from flask import Flask, request, jsonify

app = Flask(__name__)

# Function to get a database connection
def get_db_connection(db_file):
    conn = sqlite3.connect(db_file)
    conn.row_factory = sqlite3.Row  # Return rows as dictionaries
    return conn

@app.route('/')
def home():
    return "Hello, Flask! This is the home page."

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

if __name__ == '__main__':
    print("Starting Flask server...")
    app.run(debug=True, port=5001)

