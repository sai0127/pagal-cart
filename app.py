#basic setup flask

from flask import Flask, jsonify,request
import sqlite3
import bcrypt

app = Flask(__name__)


# add a function to connect to database

def get_db():
    conn = sqlite3.connect('learn.db')
    conn.row_factory= sqlite3.Row
    return conn

#adding Route
@app.route('/')
def home():
    return "Flask is working"


#create a databse file

def create_table():
    db = get_db()
    cursor = db.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users(
                   id INTEGER PRIMARY KEY,
                   name TEXT,
                   email TEXT,
                   password TEXT       
        )

    ''')
    db.commit()
    db.close()
create_table()

@app.route('/users', methods=['POST'])
def add_user():
    data = request.json
    db = get_db()
    cursor = db.cursor()
    cursor.execute('INSERT INTO users (name, email, password) VALUES (?, ?, ?)',
                   (data['name'], data['email'], data['password']))
    db.commit()
    db.close()
    return jsonify({"message": "user added!"})

#delete the user
@app.route('/users/<id>', methods=['DELETE'])
def delete_user(id):
    data = request.json
    db = get_db()
    cursor = db.cursor()
    cursor.execute('DELETE FROM users WHERE id = ?', (id,))
    db.commit()

    db.close()
    return jsonify({"message": "user deleted"})

#update
@app.route('/users/<id>',methods = ['PUT'])
def update_user(id):
    data = request.json
    db = get_db()
    cursor= db.cursor()
    cursor.execute('UPDATE users SET name =?, email=? WHERE id =?',
                   (data['name'],data['email'],id))
    db.commit()
    db.close()
    return jsonify({"message":"user update"})

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
        token = create_access_token(identity=str(user['id']))
        return jsonify({
            "message": "login successful!", 
            "token": token,
            "role": user['role']
            })
    else:
        return jsonify({"message": "invalid credentials"})



#add get route to read users from database
@app.route('/users')
def get_users():
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT * FROM users')
    users = cursor.fetchall()
    db.close()
    return jsonify([dict(user)for user in users])





if __name__ == '__main__':
    app.run(debug=True)