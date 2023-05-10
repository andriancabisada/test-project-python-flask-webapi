from flask import Flask, jsonify, request
from flask_mysqldb import MySQL
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
from flask_wtf.csrf import CSRFProtect
from flask_caching import Cache
from flask_bcrypt import Bcrypt


app = Flask(__name__)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'admin'
app.config['MYSQL_PASSWORD'] = 'password'
app.config['MYSQL_DB'] = 'mydatabase'


cache = Cache(app, config={'CACHE_TYPE': 'simple'})

# Update with your own secret key
app.config['JWT_SECRET_KEY'] = 'super-secret-key'
mysql = MySQL(app)
jwt = JWTManager(app)

# Initialize CSRF protection
csrf = CSRFProtect(app)

# encryption
bcrypt = Bcrypt()


# initialize sql
db = SQLAlchemy()


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    products = db.relationship('Product', backref='user', lazy=True)

    def __repr__(self):
        return f"User(id={self.id}, username='{self.username}')"


class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    products = db.relationship('Product', backref='category', lazy=True)

    def __repr__(self):
        return f"Category(id={self.id}, name='{self.name}')"


class Product(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey(
        'categories.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    def __repr__(self):
        return f"Product(id={self.id}, name='{self.name}', category_id={self.category_id}, user_id={self.user_id})"


@app.route('/register', methods=['POST'])
def register():
    # get the request data
    data = request.get_json()

    # check if the username and password are provided in the request
    if not data.get('username') or not data.get('password'):
        return jsonify({'error': 'Missing username or password'}), 400

    # check if the username already exists in the database
    existing_user = User.query.filter_by(username=data['username']).first()
    if existing_user:
        return jsonify({'error': 'Username already exists'}), 400

    # create a new user object and hash the password using bcrypt
    password_hash = bcrypt.generate_password_hash(
        data['password']).decode('utf-8')
    new_user = User(username=data['username'], password=password_hash)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'User registered successfully'}), 201

# Login endpoint


@app.route('/login', methods=['POST'])
@csrf.protect
def login():

    username = request.json.get('username', None)
    password = request.json.get('password', None)
    if not username or not password:
        return jsonify({'msg': 'Please provide both username and password'}), 400

    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM users WHERE username = %s", [username])
    user = cur.fetchone()
    cur.close()

    if not user or not bcrypt.check_password_hash(user[2], password):
        return jsonify({'msg': 'Invalid username or password'}), 401

    access_token = create_access_token(identity=user[0])
    return jsonify({'access_token': access_token}), 200


# Logout endpoint
@app.route('/logout', methods=['POST'])
@csrf.protect
@jwt_required()
def logout():

    return jsonify({'message': 'User logged out successfully'})


@app.route('/products')
@jwt_required()
@cache.cached(timeout=300)  # Cache the response for 5 minutes
@csrf.exempt  # Exempt this endpoint from CSRF protection
def get_products():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM products")
    rows = cur.fetchall()
    products = []
    for row in rows:
        product = {
            'id': row[0],
            'name': row[1],
            'description': row[2],
            'category_id': row[3]
        }
        products.append(product)
    return jsonify(products), 200


@app.route('/products/<int:product_id>')
@jwt_required()
@cache.cached(timeout=300)  # Cache the response for 5 minutes
def get_product(product_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM products WHERE id = %s", [product_id])
    product = cur.fetchone()
    if not product:
        return jsonify({'error': 'Product not found'}), 404
    # check if the user is authorized to access the product
    user_id = get_jwt_identity()
    if user_id != product['user_id']:
        return jsonify({'error': 'Unauthorized access'}), 403
    # return the product details
    return jsonify({
        'id': product['id'],
        'name': product['name'],
        'description': product['description'],
        'category_id': product['category_id']
    }), 200


@app.route('/products', methods=['POST'])
@jwt_required()
def create_product():

    # get the request data
    data = request.get_json()

    # check if the required fields are present in the request
    if not data.get('name') or not data.get('description') or not data.get('category_id'):
        return jsonify({'error': 'Missing required fields'}), 400

    # check if the category exists
    category = Category.query.get(data['category_id'])
    if not category:
        return jsonify({'error': 'Invalid category ID'}), 400

    # create a new product object and add it to the database
    product = Product(name=data['name'], description=data['description'],
                      category_id=data['category_id'], user_id=get_jwt_identity())
    db.session.add(product)
    db.session.commit()

    return jsonify({'message': 'Product created successfully', 'product': product}), 201


@app.route('/products/<int:product_id>', methods=['PUT'])
@jwt_required()
def update_product(product_id):
    name = request.json['name']
    description = request.json['description']
    category_id = request.json['category_id']
    cur = mysql.connection.cursor()
    cur.execute("UPDATE products SET name = %s, description = %s, category_id = %s WHERE id = %s",
                (name, description, category_id, product_id))
    mysql.connection.commit()
    return jsonify({'success': 'Product updated successfully'}), 200


@app.route('/products/<int:product_id>', methods=['DELETE'])
@jwt_required()
def delete_product(product_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM products WHERE id = %s", [product_id])
    product = cur.fetchone()
    if not product:
        return jsonify({'error': 'Product not found'}), 404
    # check if the user is authorized to access the product
    user_id = get_jwt_identity()
    if user_id != product['user_id']:
        return jsonify({'error': 'Unauthorized access'}), 403

    cur.execute("DELETE FROM products WHERE id = %s", [product_id])
    mysql.connection.commit()
    return jsonify({'success': 'Product deleted successfully'}), 200


@app.route('/categories')
@jwt_required()
@cache.cached(timeout=300)
@csrf.exempt  # Exempt this endpoint from CSRF protection
def get_categories():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM categories")
    rows = cur.fetchall()
    categories = []
    for row in rows:
        category = {
            'id': row[0],
            'name': row[1]
        }
        categories.append(category)

    return jsonify(categories), 200


@app.route('/categories/int:category_id')
@jwt_required()
@cache.cached(timeout=300)
@csrf.exempt  # Exempt this endpoint from CSRF protection
def get_category(category_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM categories WHERE id = %s", [category_id])
    row = cur.fetchone()
    if not row:
        return jsonify({'error: Category not foound'}), 404

    user_id = get_jwt_identity()
    if user_id != row['user_id']:
        return jsonify({'error': 'Unauthorized access'}), 403

    return jsonify({
        'id': row['id'],
        'name': row['name']
    }), 200


@app.route('/categories', methods=['POST'])
@jwt_required()
def create_category():
    name = request.json['name']
    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO categories (name) VALUES (%s)", [name])
    mysql.connection.commit()
    return jsonify({'success': 'Category created successfully'}), 201


@app.route('/categories/int:category_id', methods=['PUT'])
@jwt_required()
def update_category(category_id):
    name = request.json['name']
    cur = mysql.connection.cursor()
    cur.execute("UPDATE categories SET name = %s WHERE id = %s",
                (name, category_id))
    mysql.connection.commit()
    return jsonify({'success': 'Category updated successfully'}), 200


@app.route('/categories/int:category_id', methods=['DELETE'])
@jwt_required()
def delete_category(category_id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM categories WHERE id = %s", [category_id])
    mysql.connection.commit()
    return jsonify({'success': 'Category deleted successfully'}), 200


if __name__ == '__main__':
    app.run(debug=True)
