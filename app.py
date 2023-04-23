from flask import Flask, jsonify, request
from flask_mysqldb import MySQL


app = Flask(__name__)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'admin'
app.config['MYSQL_PASSWORD'] = 'password311'
app.config['MYSQL_DB'] = 'mydatabase'
mysql = MySQL(app)


@app.route('/products')
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
def get_product(product_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM products WHERE id = %s", [product_id])
    row = cur.fetchone()
    if row:
        product = {
            'id': row[0],
            'name': row[1],
            'description': row[2],
            'category_id': row[3]
        }
        return jsonify(product)
    else:
        return jsonify({'error': 'Product not found'})


@app.route('/products', methods=['POST'])
def create_product():
    name = request.json['name']
    description = request.json['description']
    category_id = request.json['category_id']
    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO products (name, description, category_id) VALUES (%s, %s, %s)", (name, description, category_id))
    mysql.connection.commit()
    return jsonify({'success': 'Product created successfully'})

@app.route('/products/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    name = request.json['name']
    description = request.json['description']
    category_id = request.json['category_id']
    cur = mysql.connection.cursor()
    cur.execute("UPDATE products SET name = %s, description = %s, category_id = %s WHERE id = %s", (name, description, category_id, product_id))
    mysql.connection.commit()
    return jsonify({'success': 'Product updated successfully'})

@app.route('/products/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM products WHERE id = %s", [product_id])
    mysql.connection.commit()
    return jsonify({'success': 'Product deleted successfully'})

@app.route('/categories')
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
def create_category():
    name = request.json['name']
    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO categories (name) VALUES (%s)", [name])
    mysql.connection.commit()
    return jsonify({'success': 'Category created successfully'})

@app.route('/categories/int:category_id', methods=['PUT'])
def update_category(category_id):
    name = request.json['name']
    cur = mysql.connection.cursor()
    cur.execute("UPDATE categories SET name = %s WHERE id = %s", (name, category_id))
    mysql.connection.commit()
    return jsonify({'success': 'Category updated successfully'})

@app.route('/categories/int:category_id', methods=['DELETE'])
def delete_category(category_id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM categories WHERE id = %s", [category_id])
    mysql.connection.commit()
    return jsonify({'success': 'Category deleted successfully'})


if __name__ == '__main__':
    app.run(debug=True)
