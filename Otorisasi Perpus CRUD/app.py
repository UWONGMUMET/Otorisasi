from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
import secrets

app = Flask(__name__)

app.config['JWT_SECRET_KEY'] = secrets.token_hex(16)
jwt = JWTManager(app)

users = [
    {"username": "penjaga", "password": "penjaga123", "role": "penjaga_perpus"},
    {"username": "pembaca", "password": "pembaca123", "role": "pembaca"}
]

books = [
    {"id": 1, "title": "Python for Beginners", "author": "John Doe"},
    {"id": 2, "title": "Flask API Development", "author": "Jane Smith"}
]

@app.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        username = data.get('username')
        password = data.get('password')

        user = next((user for user in users if user['username'] == username and user['password'] == password), None)
        if not user:
            return jsonify({"error": "Invalid username or password"}), 401
        
        access_token = create_access_token(identity={"username": username, "role": user["role"]})
        return jsonify({"access_token": access_token}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route('/books', methods=['GET'])
@jwt_required()
def get_books():
    try:
        return jsonify(books), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route('/books', methods = ['POST'])
@jwt_required()
def add_book():
    try:
        current_user = get_jwt_identity()
        if current_user["role"]!= "penjaga_perpus":
            return jsonify({"error": "Unauthorized access"}), 401
        
        new_book = request.get_json()
        if not new_book or 'title' not in new_book or 'author' not in new_book:
            return jsonify({"error": "Invalid book data"}), 400
        
        new_book['id'] = len(books) + 1
        books.append(new_book)
        return jsonify(new_book), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/books/<int:book_id>', methods=['PUT'])
@jwt_required()
def update_book(book_id):
    try:
        current_user = get_jwt_identity()
        if current_user["role"]!= "penjaga_perpus":
            return jsonify({"error": "Unauthorized access"}), 401
        
        book = next((book for book in books if book['id'] == book_id), None)
        if not book:
            return jsonify({"error": "Book not found"}), 404
        
        updated_book = request.get_json()
        if not updated_book:
            return jsonify({"error": "No data provided"}), 400
        
        if 'title' in updated_book:
            book['title'] = updated_book['title']
        if 'author' in updated_book:
            book['author'] = updated_book['author']
        
        return jsonify(book), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/books/<int:book_id>', methods=['DELETE'])
@jwt_required()
def delete_book(book_id):
    try:
        current_user = get_jwt_identity()
        if current_user["role"]!= "penjaga_perpus":
            return jsonify({"error": "Unauthorized access"}), 401
        
        book = next((book for book in books if book['id'] == book_id), None)
        if not book:
            return jsonify({"error": "Book not found"}), 404
        
        books.remove(book)
        return jsonify({"message": "Book deleted successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)