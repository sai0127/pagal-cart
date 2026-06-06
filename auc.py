
from flask import Flask, jsonify,request
import sqlite3
import bcrypt
from flask_cors import CORS


app = Flask(__name__)
CORS(app)


# add a function to connect to database

def get_db():
    conn = sqlite3.connect('learn.db')
    conn.row_factory= sqlite3.Row
    return conn

#adding Route
@app.route('/')
def home():
    return "Flask is working"

def create_table():
    db = get_db()
    cursor = db.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            name TEXT,
            email TEXT,
            password TEXT
        )
    ''')
    db.commit()
    db.close()
create_table()



#sinup
@app.route('/signup', methods=['POST'])
def sinup():
    data = request.json
    hashed = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    db = get_db()
    cursor = db.cursor()
    cursor.execute('INSERT INTO users (name,email,password) VALUES(?,?,?)',
                   (data['name'],data['email'],hashed))
    db.commit()
    db.close()
    return jsonify({"message":"user created"})

#login
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    db = get_db()
    cursor = db.cursor()
    
    # find user by email
    cursor.execute('SELECT * FROM users WHERE email = ?', (data['email'],))
    user = cursor.fetchone()
    db.close()
    
    # check if user exists and password matches
    if user and bcrypt.checkpw(data['password'].encode('utf-8'), user['password'].encode('utf-8')):
        return jsonify({"message": "login successful!"})
    else:
        return jsonify({"message": "invalid credentials"})






if __name__ == '__main__':
    app.run(debug=True)