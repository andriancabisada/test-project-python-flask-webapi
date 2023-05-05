from flask import Flask, jsonify, request
from flask_mysqldb import MySQL
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
from flask_wtf.csrf import CSRFProtect
from flask_caching import Cache


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

# Login endpoint


@app.route('/login', methods=['POST'])
@csrf.protect
def login():
    username = request.json['username']
    password = request.json['password']

    # Check if username and password are valid
    if username == 'myusername' and password == 'mypassword':
        access_token = create_access_token(identity=username)
        return jsonify({'access_token': access_token})
    else:
        return jsonify({'error': 'Invalid username or password'})

# Logout endpoint


@app.route('/logout', methods=['POST'])
@csrf.protect
@jwt_required()
def logout():
    # Simply return a message indicating that the user has logged out
    return jsonify({'message': 'User logged out successfully'})


@app.route('/products')
@jwt_required()
@cache.cached(timeout=300)  # Cache the response for 5 minutes
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
    return jsonify(products)


@app.route('/products/<int:product_id>')
@jwt_required()
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
    })


@app.route('/products', methods=['POST'])
@jwt_required()
def create_product():
    name = request.json['name']
    description = request.json['description']
    category_id = request.json['category_id']
    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO products (name, description, category_id) VALUES (%s, %s, %s)",
                (name, description, category_id))
    mysql.connection.commit()
    return jsonify({'success': 'Product created successfully'}), 201


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
    return jsonify({'success': 'Product updated successfully'})


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
    return jsonify({'success': 'Product deleted successfully'})


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

    return jsonify(categories)


@app.route('/categories/int:category_id')
@jwt_required()
@cache.cached(timeout=300)
@csrf.exempt  # Exempt this endpoint from CSRF protection
def get_category(category_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM categories WHERE id = %s", [category_id])
    row = cur.fetchone()
    if row:
        category = {
            'id': row[0],
            'name': row[1]
        }
        return jsonify(category)
    else:
        return jsonify({'error': 'Category not found'})


@app.route('/categories', methods=['POST'])
@jwt_required()
def create_category():
    name = request.json['name']
    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO categories (name) VALUES (%s)", [name])
    mysql.connection.commit()
    return jsonify({'success': 'Category created successfully'})


@app.route('/categories/int:category_id', methods=['PUT'])
@jwt_required()
def update_category(category_id):
    name = request.json['name']
    cur = mysql.connection.cursor()
    cur.execute("UPDATE categories SET name = %s WHERE id = %s",
                (name, category_id))
    mysql.connection.commit()
    return jsonify({'success': 'Category updated successfully'})


@app.route('/categories/int:category_id', methods=['DELETE'])
@jwt_required()
def delete_category(category_id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM categories WHERE id = %s", [category_id])
    mysql.connection.commit()
    return jsonify({'success': 'Category deleted successfully'})


if __name__ == '__main__':
    app.run(debug=True)
