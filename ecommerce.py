from flask import render_template
from flask import Flask,jsonify,request
from flask_cors import CORS
import sqlite3
import bcrypt

app = Flask(__name__)
CORS(app)
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity

app.config['JWT_SECRET_KEY'] = 'your-secret-key'
jwt = JWTManager(app)


def get_db():
    conn = sqlite3.connect('ecommerce.db')
    conn.row_factory = sqlite3.Row
    return conn

def create_table():
    db = get_db()
    cursor = db.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            name TEXT,
            email TEXT,
            password TEXT,
            role TEXT DEFAULT 'user'
        )
    ''')
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN role TEXT DEFAULT 'user'")
        db.commit()
    except:
        pass


    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY,
            name TEXT,
            description TEXT,
            price REAL,
            image TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cart (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            product_id INTEGER,
            quantity INTEGER
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            total REAL,
            date TEXT
        )
    ''')
    db.commit()
    db.close()
create_table()


@app.route('/')
def landing():
    return render_template('landing.html')

@app.route('/shop')
def shop():
    return render_template('index.html')

@app.route('/cart')
def cart():
    return render_template('cart.html')

@app.route('/login')
def login_page():
    return render_template('login.html')

@app.route('/signup')
def signup_page():
    return render_template('signup.html')

@app.route('/admin')
def admin():
    return render_template('admin.html')

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
    cursor.execute('SELECT * FROM users WHERE email = ?', (data['email'],))
    user = cursor.fetchone()
    db.close()
    
    if user and bcrypt.checkpw(data['password'].encode('utf-8'), user['password'].encode('utf-8')):
        token = create_access_token(identity=str(user['id']))
        return jsonify({"message": "login successful!", "token": token,"role": user['role']})
    else:
        return jsonify({"message": "invalid credentials"})


@app.route('/products',methods=['POST'])
def add_product():
    data = request.json
    db=get_db()
    cursor = db.cursor()
    cursor.execute('INSERT INTO products (name, description, price, image) VALUES(?,?,?,?)',
               (data['name'], data['description'], data['price'], data['image']))
    db.commit()
    db.close()
    return jsonify({"message": "product added"})

#get all products
@app.route('/products',methods=['GET'])
def get_products():
    db =get_db()
    cursor=db.cursor()
    cursor.execute('SELECT*FROM products')
    products = cursor.fetchall()
    db.close()
    return jsonify([dict(product) for product in products])


#cart route

@app.route('/cart', methods=['POST'])
def add_cart():
    data = request.json
    db = get_db()
    cursor = db.cursor()
    
    # check if item already in cart
    cursor.execute('SELECT * FROM cart WHERE user_id=? AND product_id=?',
                   (data['user_id'], data['product_id']))
    existing = cursor.fetchone()
    
    if existing:
        # update quantity
        cursor.execute('UPDATE cart SET quantity = quantity + 1 WHERE user_id=? AND product_id=?',
                       (data['user_id'], data['product_id']))
    else:
        # insert new
        cursor.execute('INSERT INTO cart(user_id,product_id,quantity) VALUES (?,?,?)',
                       (data['user_id'], data['product_id'], data['quantity']))
    
    db.commit()
    db.close()
    return jsonify({"message": "item added to cart"})
#get all cart items
@app.route('/cart/<user_id>',methods=['GET'])
def get_cart(user_id):
    db=get_db()
    cursor=db.cursor()
    cursor.execute('''
        SELECT cart.id, cart.quantity, products.name, products.price, products.image
        FROM cart
        JOIN products ON cart.product_id = products.id
        WHERE cart.user_id = ?
    ''', (user_id,))
    cart = cursor.fetchall()
    db.close()
    return jsonify([dict(c) for c in cart])

#remove item from cart
@app.route('/cart/delete/<id>', methods=['DELETE'])
def delete_cart(id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute('DELETE FROM cart WHERE id=?',(id,))
    db.commit()
    db.close()
    return jsonify({"messsage":"item removed"})

#place an order
@app.route('/orders',methods=['POST'])
def place_order():
    data = request.json
    db = get_db()
    cursor=db.cursor()
    cursor.execute('INSERT INTO orders(user_id,total) VALUES (?,?)',
                   (data['user_id'],data['total']))
    db.commit()
    db.close()
    return jsonify({"message":"placed an order"})


#get all orders from a user
@app.route('/orders/<user_id>',methods=['GET'])
def get_orders(user_id):
    db =get_db()
    cursor = db.cursor()
    cursor.execute('SELECT * FROM orders WHERE user_id =?',(user_id,))
    orders = cursor.fetchall()
    db.close()
    return jsonify([dict(order) for order in orders])

@app.route('/cart/update/<id>', methods=['PUT'])
def update_qty(id):
    data = request.json
    db = get_db()
    cursor = db.cursor()
    
    if data['action'] == 'increase':
        cursor.execute('UPDATE cart SET quantity = quantity + 1 WHERE id = ?', (id,))
    else:
        cursor.execute('UPDATE cart SET quantity = quantity - 1 WHERE id = ?', (id,))
    
    db.commit()
    db.close()
    return jsonify({"message": "quantity updated"})

@app.route('/products/<id>', methods=['DELETE'])
def delete_product(id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute('DELETE FROM products WHERE id = ?', (id,))
    db.commit()
    db.close()
    return jsonify({"message": "product deleted"})


@app.route('/products/<id>', methods=['PUT'])
def update_product(id):
    data = request.json
    db = get_db()
    cursor = db.cursor()
    cursor.execute('UPDATE products SET name=?, description=?, price=?, image=? WHERE id=?',
                   (data['name'], data['description'], data['price'], data['image'], id))
    db.commit()
    db.close()
    return jsonify({"message": "product updated"})

@app.route('/users/role/<id>', methods=['PUT'])
def update_role(id):
    data = request.json
    db = get_db()
    cursor = db.cursor()
    cursor.execute('UPDATE users SET role=? WHERE id=?',
                   (data['role'], id))
    db.commit()
    db.close()
    return jsonify({"message": "role updated"})
@app.route('/users', methods=['GET'])
def get_users():
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT id, name, email, role FROM users')
    users = cursor.fetchall()
    db.close()
    return jsonify([dict(user) for user in users])



if __name__ == '__main__':
    app.run(debug=True)