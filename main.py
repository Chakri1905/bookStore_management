from flask import Flask, request, jsonify, make_response
import mysql.connector
import jwt
import datetime
from functools import wraps

app = Flask(__name__)

mysql_config = {
    'host': 'localhost',
    'user': 'chakriuser',
    'password': 'Chakri@1905',
    'database': 'bookstoredata'
}

app.config['SECRET_KEY'] = 'chakri123'

def get_db_connection():
    conn = mysql.connector.connect(**mysql_config)
    return conn

def generate_token(username):
    token = jwt.encode({'username': username, 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)}, app.config['SECRET_KEY'])
    return token

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')

        if not token:
            return jsonify({'message': 'Token is missing'}), 401

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'])
        except:
            return jsonify({'message': 'Token is invalid'}), 401

        return f(*args, **kwargs)

    return decorated

@app.route('/login', methods=['POST'])
def login():
    auth = request.authorization

    if not auth or not auth.username or not auth.password:
        return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic realm="Login required!"'})

    if auth.username == 'username' and auth.password == 'password':
        token = generate_token(auth.username)
        return jsonify({'token': token})

    return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic realm="Login required!"'})


@app.route('/books', methods=['POST'])
def add_book():
    data = request.get_json()
    title = data['title']
    author = data['author']
    isbn = data['isbn']
    price = data['price']
    quantity = data['quantity']

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO bookdata (title, author, isbn, price, quantity) VALUES (%s, %s, %s, %s, %s)',
                   (title, author, isbn, price, quantity))
    conn.commit()
    conn.close()

    return jsonify({'message': 'Book added successfully'}), 201

@app.route('/books', methods=['GET'])
def get_books():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM bookdata')
    books = cursor.fetchall()
    conn.close()

    return jsonify([{'id': book[0], 'title': book[1], 'author': book[2], 'isbn': book[3], 'price': book[4], 'quantity': book[5]} for book in books])


@app.route('/books/<isbn>', methods=['GET'])
def get_book(isbn):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM bookdata WHERE isbn = %s', (isbn,))
    book = cursor.fetchone()
    conn.close()

    if book:
        return jsonify({'id': book[0], 'title': book[1], 'author': book[2], 'isbn': book[3], 'price': book[4], 'quantity': book[5]}), 200
    else:
        return jsonify({'message': 'Book not found'}), 404


@app.route('/books/<isbn>', methods=['PUT'])
@token_required
def update_book(isbn):
    data = request.get_json()
    price = data['price']
    quantity = data['quantity']

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE bookdata SET price = %s, quantity = %s WHERE isbn = %s', (price, quantity, isbn))
    conn.commit()
    conn.close()

    return jsonify({'message': 'Book updated successfully'}), 200


@app.route('/books/<isbn>', methods=['DELETE'])
@token_required
def delete_book(isbn):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM bookdata WHERE isbn = %s', (isbn,))
    conn.commit()
    conn.close()

    return jsonify({'message': 'Book deleted successfully'}), 200



if __name__ == '__main__':
    app.run(debug=True)
