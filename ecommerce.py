from flask import render_template
from flask import Flask,jsonify,request
from flask import render_template, send_from_directory
from datetime import timedelta
from flask_cors import CORS
import sqlite3
import bcrypt

app = Flask(__name__)
CORS(app)
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
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
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS order_items (
        id INTEGER PRIMARY KEY,
        order_id INTEGER,
        product_id INTEGER,
        quantity INTEGER,
        price REAL
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

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')



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
        return jsonify({"message": "login successful!", "token": token,"role": user['role'], "name":user['name'],"id":user['id']})
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
#place an order
@app.route('/orders', methods=['POST'])
def place_order():
    data = request.json
    db = get_db()
    cursor = db.cursor()
    
    # create order
    cursor.execute('INSERT INTO orders(user_id, total) VALUES (?,?)',
                   (data['user_id'], data['total']))
    order_id = cursor.lastrowid
    
    # save each cart item to order_items
    for item in data['items']:
        cursor.execute('INSERT INTO order_items(order_id, product_id, quantity, price) VALUES (?,?,?,?)',
                       (order_id, item['product_id'], item['quantity'], item['price']))
    
    # clear cart after order
    cursor.execute('DELETE FROM cart WHERE user_id=?', (data['user_id'],))
    
    db.commit()
    db.close()
    return jsonify({"message": "order placed!"})


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

@app.route('/order-items/<order_id>', methods=['GET'])
def get_order_items(order_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute('''
        SELECT order_items.quantity, order_items.price,
               products.name, products.image
        FROM order_items
        JOIN products ON order_items.product_id = products.id
        WHERE order_items.order_id = ?
    ''', (order_id,))
    items = cursor.fetchall()
    db.close()
    return jsonify([dict(item) for item in items])



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

@app.route('/stats', methods=['GET'])
def get_stats():
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT COUNT(*) FROM products')
    products = cursor.fetchone()[0]
    cursor.execute('SELECT COUNT(*) FROM users')
    users = cursor.fetchone()[0]
    cursor.execute('SELECT COUNT(*) FROM orders')
    orders = cursor.fetchone()[0]
    db.close()
    return jsonify({"products": products, "users": users, "orders": orders})




def seed_products():
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT COUNT(*) FROM products')
    count = cursor.fetchone()[0]
    
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
        cursor.executemany('INSERT INTO products (name, description, price, image) VALUES (?,?,?,?)', products)
        db.commit()
    db.close()
def reset_products():
    db = get_db()
    cursor = db.cursor()
    cursor.execute('DELETE FROM products')
    db.commit()
    db.close()


seed_products()







if __name__ == '__main__':
    app.run(debug=True)