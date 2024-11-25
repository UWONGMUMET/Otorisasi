from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
import secrets

app = Flask(__name__)

app.config['JWT_SECRET_KEY'] = secrets.token_hex(32) 
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
            return jsonify({"message": "Missing JSON body"}), 400
        
        username = data.get('username')
        password = data.get('password')

        user = next((u for u in users if u['username'] == username and u['password'] == password), None)
        if not user:
            return jsonify({"message": "Invalid username or password"}), 401

        access_token = create_access_token(identity={"username": username, "role": user["role"]})
        return jsonify({"access_token": access_token}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/books', methods=['GET'])
@jwt_required()
def get_books():
    return jsonify(books), 200

@app.route('/books', methods=['POST'])
@jwt_required()
def add_book():
    try:
        current_user = get_jwt_identity()
        if current_user['role'] != 'penjaga_perpus':
            return jsonify({"error": "Unauthorized"}), 403

        new_book = request.get_json()
        if not new_book:
            return jsonify({"message": "Missing JSON body"}), 400
        
        new_book["id"] = len(books) + 1
        books.append(new_book)
        return jsonify(new_book), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
