Test Project for Python Flask API

This is a RESTful API for managing products and categories. The API is built using Flask and uses a MySQL database for storage. JWT authentication is used for user authentication and access control.

Installation

    Clone the repository: git clone https://github.com/andriancabisada/test-project-python-flask-webapi
    Install dependencies: pip install -r requirements.txt
    Configure database: create database database_name and set the credentials in app.py.
    Run the application: python app.py
    Access the API at http://localhost:5000/

Endpoints

Products
GET /products

Get a list of all products.

Request parameters:
    None.

Response:

    200 OK on success.
    [
        {
        "id": 1,
        "name": "Product 1",
        "description": "This is the first product",
        "category": {
                "id": 1,
                "name": "Category 1"
            }
        },
        {
        "id": 2,
        "name": "Product 2",
        "description": "This is the second product",
        "category": {
                "id": 2,
                "name": "Category 2"
            }
        }
    ]

GET /products/{id}

Get a specific product by ID.

Request parameters:

    id - The ID of the product to retrieve.

Response:

    200 OK on success.
    404 Not Found if the product with the specified ID does not exist.

    {
        "id": 1,
        "name": "Product 1",
        "description": "This is the first product",
        "category": {
            "id": 1,
            "name": "Category 1"
        }
    }

POST /products

Create a new product.

Request parameters:

    name - The name of the product.
    description - The description of the product.
    category_id - The ID of the category to which the product belongs.

Response:

    201 Created on success.
    400 Bad Request if the request is invalid.

{
    "id": 3,
    "name": "Product 3",
    "description": "This is the third product",
    "category": {
        "id": 1,
        "name": "Category 1"
    }
}

PUT /products/{id}

Update an existing product.

Request parameters:

    id - The ID of the product to update.
    name - The new name of the product.
    description - The new description of the product.
    category_id - The new ID of the category to which the product belongs.

Response:

    200 OK on success.
    400 Bad Request if the request is invalid.
    404 Not Found if the product with the specified ID does not exist.

{
    "id": 1,
    "name": "Updated Product 1",
    "description": "This is an updated product",
    "category": {
        "id": 1,
        "name": "Category 1"
    }
}

DELETE /products/{id}

Delete a product.

Request parameters:

    id - The ID of the product to delete.

Response:

    200 OK on success.
    404 Not Found if the product with the specified ID does not exist.

    {
        "success": "Product deleted successfully"
    }


Category endpoint

This endpoint allows you to perform CRUD operations on categories.
GET /categories

Returns a list of all categories.

Response

    200 OK: Returns a JSON array of category objects. Each category object has the following fields:
        id (int): The ID of the category.
        name (str): The name of the category.

Example:

    [
        {
            "id": 1,
            "name": "Electronics"
        },
        {
            "id": 2,
            "name": "Books"
        },
        ...
    ]


GET /categories/{category_id}

Returns a single category by ID.

Parameters

    category_id (int): The ID of the category.

Response

    200 OK: Returns a JSON object with the following fields:
        id (int): The ID of the category.
        name (str): The name of the category.

Example:

    {
        "id": 1,
        "name": "Electronics"
    }

    404 Not Found: If the category with the specified ID does not exist.

POST /categories

Creates a new category.

Request Body

    name (str): The name of the category.

Example:

{
    "name": "Clothing"
}

Response

    201 Created: Returns a JSON object with the following fields:
        id (int): The ID of the new category.
        name (str): The name of the new category.

Example:

    {
        "id": 4,
        "name": "Clothing"
    }

    400 Bad Request: If the request body is invalid.

PUT /categories/{category_id}

Updates an existing category.

Parameters

    category_id (int): The ID of the category to update.

Request Body

    name (str): The new name of the category.

Example:

    {
        "name": "New Electronics"
    }

Response

    200 OK: Returns a JSON object with the following fields:
        id (int): The ID of the updated category.
        name (str): The new name of the category.

Example:

    {
        "id": 1,
        "name": "New Electronics"
    }

    400 Bad Request: If the request body is invalid.
    404 Not Found: If the category with the specified ID does not exist.

DELETE /categories/{category_id}

Deletes a category.

Parameters

    category_id (int): The ID of the category to delete.

Response

    204 No Content: If the category is deleted successfully.

    404 Not Found: If the category with the specified ID does not exist.