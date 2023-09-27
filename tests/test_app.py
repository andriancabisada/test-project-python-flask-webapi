import pytest
from app import app, db  # Import your Flask app and SQLAlchemy db
from flask_jwt_extended import create_access_token

# Initialize the app for testing
app.config['TESTING'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'  # Use an in-memory SQLite database for testing
client = app.test_client()

@pytest.fixture
def access_token():
    # Create a test JWT access token for testing protected routes
    with app.app_context():
        access_token = create_access_token(identity=1)
        yield access_token

def test_register():
    response = client.post('/register', json={'username': 'testuser', 'password': 'testpassword'})
    assert response.status_code == 201
    assert 'User registered successfully' in response.json['message']

def test_login():
    response = client.post('/login', json={'username': 'testuser', 'password': 'testpassword'})
    assert response.status_code == 200
    assert 'access_token' in response.json

def test_get_products(access_token):
    response = client.get('/products', headers={'Authorization': f'Bearer {access_token}'})
    assert response.status_code == 200
    assert isinstance(response.json, list)

def test_create_product(access_token):
    data = {'name': 'Test Product', 'description': 'Test Description', 'category_id': 1}
    response = client.post('/products', json=data, headers={'Authorization': f'Bearer {access_token}'})
    assert response.status_code == 201
    assert 'Product created successfully' in response.json['message']

# Add more test cases for other routes and functionality as needed

if __name__ == '__main__':
    pytest.main()
