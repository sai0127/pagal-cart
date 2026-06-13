from flask import render_template
from flask import Flask, jsonify, request
from flask import render_template, send_from_directory
from datetime import timedelta
from flask_cors import CORS
import bcrypt
import os
import psycopg2
import psycopg2.extras
import resend
import random


app = Flask(__name__)
CORS(app)

from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity


resend.api_key = os.environ.get('RESEND_API_KEY')
# ─── DATABASE CONNECTION ───────────────────────────────────────────────────────

def get_db():
    conn = psycopg2.connect(os.environ.get('DATABASE_URL'))
    return conn

def get_cursor(db):
    return db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)


# ─── CREATE TABLES ─────────────────────────────────────────────────────────────

def create_table():
    db = get_db()
    cursor = db.cursor()

    # users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            name TEXT,
            email TEXT,
            password TEXT,
            role TEXT DEFAULT 'user'
        )
    ''')

    # products table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id SERIAL PRIMARY KEY,
            name TEXT,
            description TEXT,
            price REAL,
            image TEXT
        )
    ''')

    # cart table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cart (
            id SERIAL PRIMARY KEY,
            user_id INTEGER,
            product_id INTEGER,
            quantity INTEGER
        )
    ''')

    # orders table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id SERIAL PRIMARY KEY,
            user_id INTEGER,
            total REAL,
            date TEXT
        )
    ''')

    # order items table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS order_items (
            id SERIAL PRIMARY KEY,
            order_id INTEGER,
            product_id INTEGER,
            quantity INTEGER,
            price REAL
        )
    ''')
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS wishlist (
            id SERIAL PRIMARY KEY,
            user_id INTEGER,
            product_id INTEGER
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS otps (
            id SERIAL PRIMARY KEY,
            email TEXT,
            otp TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    db.commit()
    db.close()

create_table()


# ─── PAGE ROUTES ───────────────────────────────────────────────────────────────

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

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/admin-login')
def admin_login_page():
    return render_template('admin-login.html')

@app.route('/address')
def address_page():
    return render_template('address.html')

@app.route('/wishlist')
def wishlist_page():
    return render_template('wishlist.html')
# ─── AUTH ROUTES ───────────────────────────────────────────────────────────────

# signup
@app.route('/signup', methods=['POST'])
def sinup():
    data = request.json
    hashed = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    db = get_db()
    cursor = get_cursor(db)
    cursor.execute('INSERT INTO users (name, email, password) VALUES (%s, %s, %s)',
                   (data['name'], data['email'], hashed))
    db.commit()
    db.close()
    return jsonify({"message": "user created"})

# login
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    db = get_db()
    cursor = get_cursor(db)
    cursor.execute('SELECT * FROM users WHERE email = %s', (data['email'],))
    user = cursor.fetchone()
    db.close()

    if user and bcrypt.checkpw(data['password'].encode('utf-8'), user['password'].encode('utf-8')):
        token = create_access_token(identity=str(user['id']))
        return jsonify({
            "message": "login successful!",
            "token": token,
            "role": user['role'],
            "name": user['name'],
            "id": user['id']
        })
    else:
        return jsonify({"message": "invalid credentials"})


# ─── PRODUCT ROUTES ────────────────────────────────────────────────────────────

# add product
@app.route('/products', methods=['POST'])
def add_product():
    data = request.json
    db = get_db()
    cursor = get_cursor(db)
    cursor.execute('INSERT INTO products (name, description, price, image) VALUES (%s, %s, %s, %s)',
                   (data['name'], data['description'], data['price'], data['image']))
    db.commit()
    db.close()
    return jsonify({"message": "product added"})

# get all products
@app.route('/products', methods=['GET'])
def get_products():
    db = get_db()
    cursor = get_cursor(db)
    cursor.execute('SELECT * FROM products')
    products = cursor.fetchall()
    db.close()
    return jsonify([dict(product) for product in products])

# update product
@app.route('/products/<id>', methods=['PUT'])
def update_product(id):
    data = request.json
    db = get_db()
    cursor = get_cursor(db)
    cursor.execute('UPDATE products SET name=%s, description=%s, price=%s, image=%s WHERE id=%s',
                   (data['name'], data['description'], data['price'], data['image'], id))
    db.commit()
    db.close()
    return jsonify({"message": "product updated"})

# delete product
@app.route('/products/<id>', methods=['DELETE'])
def delete_product(id):
    db = get_db()
    cursor = get_cursor(db)
    cursor.execute('DELETE FROM products WHERE id = %s', (id,))
    db.commit()
    db.close()
    return jsonify({"message": "product deleted"})


# ─── CART ROUTES ───────────────────────────────────────────────────────────────

# add to cart
@app.route('/cart', methods=['POST'])
def add_cart():
    data = request.json
    db = get_db()
    cursor = get_cursor(db)

    # check if item already in cart
    cursor.execute('SELECT * FROM cart WHERE user_id=%s AND product_id=%s',
                   (data['user_id'], data['product_id']))
    existing = cursor.fetchone()

    if existing:
        # update quantity
        cursor.execute('UPDATE cart SET quantity = quantity + 1 WHERE user_id=%s AND product_id=%s',
                       (data['user_id'], data['product_id']))
    else:
        # insert new item
        cursor.execute('INSERT INTO cart(user_id, product_id, quantity) VALUES (%s, %s, %s)',
                       (data['user_id'], data['product_id'], data['quantity']))

    db.commit()
    db.close()
    return jsonify({"message": "item added to cart"})

# get cart items for a user
@app.route('/cart/<user_id>', methods=['GET'])
def get_cart(user_id):
    db = get_db()
    cursor = get_cursor(db)
    cursor.execute('''
        SELECT cart.id, cart.quantity, products.name, products.price, products.image
        FROM cart
        JOIN products ON cart.product_id = products.id
        WHERE cart.user_id = %s
    ''', (user_id,))
    cart = cursor.fetchall()
    db.close()
    return jsonify([dict(c) for c in cart])

# remove item from cart
@app.route('/cart/delete/<id>', methods=['DELETE'])
def delete_cart(id):
    db = get_db()
    cursor = get_cursor(db)
    cursor.execute('DELETE FROM cart WHERE id = %s', (id,))
    db.commit()
    db.close()
    return jsonify({"message": "item removed"})

# update cart quantity
@app.route('/cart/update/<id>', methods=['PUT'])
def update_qty(id):
    data = request.json
    db = get_db()
    cursor = get_cursor(db)

    if data['action'] == 'increase':
        cursor.execute('UPDATE cart SET quantity = quantity + 1 WHERE id = %s', (id,))
    else:
        cursor.execute('UPDATE cart SET quantity = quantity - 1 WHERE id = %s', (id,))

    db.commit()
    db.close()
    return jsonify({"message": "quantity updated"})


# ─── ORDER ROUTES ──────────────────────────────────────────────────────────────

# place an order
@app.route('/orders', methods=['POST'])
def place_order():
    data = request.json
    db = get_db()
    cursor = get_cursor(db)

    # create order and get order id
    cursor.execute('INSERT INTO orders(user_id, total) VALUES (%s, %s) RETURNING id',
                   (data['user_id'], data['total']))
    order_id = cursor.fetchone()['id']

    # save each cart item to order_items
    for item in data['items']:
        cursor.execute('INSERT INTO order_items(order_id, product_id, quantity, price) VALUES (%s, %s, %s, %s)',
                       (order_id, item['product_id'], item['quantity'], item['price']))

    # clear cart after order
    cursor.execute('DELETE FROM cart WHERE user_id = %s', (data['user_id'],))

    db.commit()
    db.close()
    return jsonify({"message": "order placed!"})

# get all orders for a user
@app.route('/orders/<user_id>', methods=['GET'])
def get_orders(user_id):
    db = get_db()
    cursor = get_cursor(db)
    cursor.execute('SELECT * FROM orders WHERE user_id = %s', (user_id,))
    orders = cursor.fetchall()
    db.close()
    return jsonify([dict(order) for order in orders])

# get order items for an order
@app.route('/order-items/<order_id>', methods=['GET'])
def get_order_items(order_id):
    db = get_db()
    cursor = get_cursor(db)
    cursor.execute('''
        SELECT order_items.quantity, order_items.price,
               products.name, products.image
        FROM order_items
        JOIN products ON order_items.product_id = products.id
        WHERE order_items.order_id = %s
    ''', (order_id,))
    items = cursor.fetchall()
    db.close()
    return jsonify([dict(item) for item in items])


# ─── USER ROUTES ───────────────────────────────────────────────────────────────

# get all users
@app.route('/users', methods=['GET'])
def get_users():
    db = get_db()
    cursor = get_cursor(db)
    cursor.execute('SELECT id, name, email, role FROM users')
    users = cursor.fetchall()
    db.close()
    return jsonify([dict(user) for user in users])
# get all orders (admin)
@app.route('/all-orders', methods=['GET'])
def get_all_orders():
    db = get_db()
    cursor = get_cursor(db)
    cursor.execute('SELECT * FROM orders')
    orders = cursor.fetchall()
    db.close()
    return jsonify([dict(order) for order in orders])

# delete user
@app.route('/users/<id>', methods=['DELETE'])
def delete_user(id):
    db = get_db()
    cursor = get_cursor(db)
    cursor.execute('DELETE FROM users WHERE id = %s', (id,))
    db.commit()
    db.close()
    return jsonify({"message": "user deleted"})

# update user role
@app.route('/users/role/<id>', methods=['PUT'])
def update_role(id):
    data = request.json
    db = get_db()
    cursor = get_cursor(db)
    cursor.execute('UPDATE users SET role = %s WHERE id = %s',
                   (data['role'], id))
    db.commit()
    db.close()
    return jsonify({"message": "role updated"})


# ───   WISHLIST ROUTES  ───────────────────────────────────────────────────────────────

# add to wishlist
@app.route('/wishlist', methods=['POST'])
def add_wishlist():
    data = request.json
    db = get_db()
    cursor = get_cursor(db)
    
    # check if already in wishlist
    cursor.execute('SELECT * FROM wishlist WHERE user_id=%s AND product_id=%s',
                   (data['user_id'], data['product_id']))
    existing = cursor.fetchone()
    
    if existing:
        return jsonify({"message": "already in wishlist"})
    
    cursor.execute('INSERT INTO wishlist(user_id, product_id) VALUES (%s, %s)',
                   (data['user_id'], data['product_id']))
    db.commit()
    db.close()
    return jsonify({"message": "added to wishlist"})

# get wishlist for a user
@app.route('/wishlist/<user_id>', methods=['GET'])
def get_wishlist(user_id):
    db = get_db()
    cursor = get_cursor(db)
    cursor.execute('''
        SELECT wishlist.id, products.name, products.price, products.image, products.id as product_id
        FROM wishlist
        JOIN products ON wishlist.product_id = products.id
        WHERE wishlist.user_id = %s
    ''', (user_id,))
    items = cursor.fetchall()
    db.close()
    return jsonify([dict(item) for item in items])

# remove from wishlist
@app.route('/wishlist/<id>', methods=['DELETE'])
def delete_wishlist(id):
    db = get_db()
    cursor = get_cursor(db)
    cursor.execute('DELETE FROM wishlist WHERE id = %s', (id,))
    db.commit()
    db.close()
    return jsonify({"message": "removed from wishlist"})

#----- Email Otp-------------------------------------
# send OTP
@app.route('/send-otp', methods=['POST'])
def send_otp():
    data = request.json
    email = data['email']
    otp = str(random.randint(100000, 999999))
    
    db = get_db()
    cursor = get_cursor(db)
    cursor.execute('DELETE FROM otps WHERE email = %s', (email,))
    cursor.execute('INSERT INTO otps (email, otp) VALUES (%s, %s)', (email, otp))
    db.commit()
    db.close()
    
    # send email using resend
    params = {
        "from": "Pagal Cart <onboarding@resend.dev>",
        "to": [email],
        "subject": "Your Pagal Cart OTP",
        "html": f"""
            <h2>Welcome to Pagal Cart! 🛒</h2>
            <p>Your OTP is: <strong>{otp}</strong></p>
            <p>This OTP is valid for 10 minutes.</p>
            <p>Do not share this with anyone.</p>
        """
    }
    resend.Emails.send(params)
    
    return jsonify({"message": "OTP sent!"})
# verify OTP
@app.route('/verify-otp', methods=['POST'])
def verify_otp():
    data = request.json
    email = data['email']
    otp = data['otp']
    
    db = get_db()
    cursor = get_cursor(db)
    cursor.execute('SELECT * FROM otps WHERE email = %s AND otp = %s', (email, otp))
    record = cursor.fetchone()
    
    if record:
        # delete OTP after use
        cursor.execute('DELETE FROM otps WHERE email = %s', (email,))
        db.commit()
        db.close()
        return jsonify({"message": "OTP verified!", "success": True})
    else:
        db.close()
        return jsonify({"message": "Invalid OTP!", "success": False})

# ─── STATS ROUTE ───────────────────────────────────────────────────────────────

# get admin stats
@app.route('/stats', methods=['GET'])
def get_stats():
    db = get_db()
    cursor = get_cursor(db)
    cursor.execute('SELECT COUNT(*) as count FROM products')
    products = cursor.fetchone()['count']
    cursor.execute('SELECT COUNT(*) as count FROM users')
    users = cursor.fetchone()['count']
    cursor.execute('SELECT COUNT(*) as count FROM orders')
    orders = cursor.fetchone()['count']
    db.close()
    return jsonify({"products": products, "users": users, "orders": orders})


# ─── SEED DATA ─────────────────────────────────────────────────────────────────

# seed admin user
def seed_admin():
    db = get_db()
    cursor = get_cursor(db)
    cursor.execute('SELECT COUNT(*) as count FROM users')
    count = cursor.fetchone()['count']

    if count == 0:
        hashed = bcrypt.hashpw('admin1234'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        cursor.execute('INSERT INTO users (name, email, password, role) VALUES (%s, %s, %s, %s)',
                       ('Admin', 'admin@gmail.com', hashed, 'admin'))
        db.commit()
    db.close()

# seed products
def seed_products():
    db = get_db()
    cursor = get_cursor(db)
    cursor.execute('SELECT COUNT(*) as count FROM products')
    count = cursor.fetchone()['count']

    if count == 0:
        products = [
            ('iPhone 15', 'Latest Apple smartphone with A16 chip', 79999, 'https://images.unsplash.com/photo-1592750475338-74b7b21085ab?w=400'),
            ('iPhone 16', 'Latest Apple smartphone with A18 chip', 89999, 'https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=400'),
            ('MacBook Air M2', 'Thin and light laptop with M2 chip', 114999, 'https://images.unsplash.com/photo-1611186871348-b1ce696e52c9?w=400'),
            ('MacBook Pro M3', 'Professional laptop with M3 chip', 199999, 'https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=400'),
            ('Samsung Galaxy S24', 'Flagship Android smartphone', 74999, 'https://images.unsplash.com/photo-1610945265064-0e34e5519bbf?w=400'),
            ('OnePlus 12', 'Fast charging flagship phone', 64999, 'https://images.unsplash.com/photo-1585060544812-6b45742d762f?w=400'),
            ('Google Pixel 8', 'Best camera smartphone', 59999, 'https://images.unsplash.com/photo-1598327105666-5b89351aff97?w=400'),
            ('iPad Pro M2', 'Professional tablet with M2 chip', 89999, 'https://images.unsplash.com/photo-1544244015-0df4b3ffc6b0?w=400'),
            ('Samsung Galaxy Tab S9', 'Premium Android tablet', 64999, 'https://images.unsplash.com/photo-1561154464-82e9adf32764?w=400'),
            ('Sony WH-1000XM5', 'Premium noise cancelling headphones', 29999, 'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=400'),
            ('Bose QuietComfort 45', 'Wireless noise cancelling headphones', 24999, 'https://images.unsplash.com/photo-1546435770-a3e426bf472b?w=400'),
            ('AirPods Pro', 'Wireless noise cancelling earbuds', 24999, 'https://images.unsplash.com/photo-1600294037681-c80b4cb5b434?w=400'),
            ('Apple Watch Series 9', 'Smartwatch with health tracking', 41999, 'https://images.unsplash.com/photo-1546868871-7041f2a55e12?w=400'),
            ('Samsung Galaxy Watch 6', 'Android smartwatch with fitness tracking', 28999, 'https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=400'),
            ('Nike Air Max', 'Premium running shoes', 12999, 'https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=400'),
            ('Adidas Ultraboost', 'Comfortable running shoes', 14999, 'https://images.unsplash.com/photo-1608231387042-66d1773070a5?w=400'),
            ('Dell XPS 15', 'High performance Windows laptop', 124999, 'https://images.unsplash.com/photo-1593642632559-0c6d3fc62b89?w=400'),
            ('HP Spectre x360', 'Premium 2 in 1 laptop', 134999, 'https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=400'),
            ('Logitech MX Master 3', 'Premium wireless mouse', 8999, 'https://images.unsplash.com/photo-1527864550417-7fd91fc51a46?w=400'),
            ('Casio G-Shock', 'Rugged sports watch', 8999, 'https://images.unsplash.com/photo-1587836374828-4dbafa94cf0e?w=400'),
        ]
        cursor.executemany('INSERT INTO products (name, description, price, image) VALUES (%s, %s, %s, %s)', products)
        db.commit()
    db.close()

seed_admin()
seed_products()


if __name__ == '__main__':
    app.run(debug=True)