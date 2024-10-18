## Inventory Management API 

This is a Simple RESTful API for managing an inventory system created for completing Backend Developer Test by Pari Indonesia. The API allows users to create, read, update, and delete items and categories.

**Table of Contents**

  * [Features](#features)
  * [Requirements](#requirements)
  * [Setup and Installation](#setup-and-installation)
  * [Running the Application](#running-the-application)
  * [API Endpoints](#api-endpoints)
  * [Debugging Process](#debugging-process)
  * [Assumptions and Decisions](#assumptions-and-decisions)
  * [Future Improvements](#future-improvements)

**Features**

  * User registration and login with JWT authentication.
  * CRUD operations for items and categories.
  * Data validation and error handling.
  * Expiry time for JWT tokens set to 3 hours.

**Requirements**

  * Python 3.x
  * SQLite
  * venv-wrapper
  * PyJWT for token authentication
  * werkzeug for password hashing

**Setup and Installation**

1.  Clone this repository:

```
git clone https://github.com/JonathanKevin16/TestPari
cd TestPari
```

2.  Create a virtual environment:

```
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
```

3.  Install required packages (if any):

```
pip install -r requirements.txt
```

4.  Create a `.env` file in the root directory with the following content:

```
SECRET_KEY=your_secret_key_here
```

Replace `your_secret_key_here` with a strong secret key.

5.  Initialize your SQLite database (if necessary):

  * Add your database initialization script here if applicable.

**Running the Application**

To start the server, run:

```
python main.py 
```

The server by default will start on `http://localhost:8000`.

**API Endpoints**

| Method | Endpoint              | Description                                      |
|--------|------------------------|-------------------------------------------------|
| POST   | /register             | Register a new user                             |
| POST   | /login                | Log in an existing user                          |
| GET    | /items                 | Get a list of items                              |
| POST   | /items                 | Create a new item                                |
| GET    | /items/{id}            | Get details of a specific item                    |
| PUT    | /items/{id}            | Update a specific item                            |
| DELETE | /items/{id}            | Delete a specific item                            |

## User Registration

Before logging in, users must register an account. Follow the steps below to register.

### Registering a New User

1. **Register a New User** using the `/register` endpoint.
   - **Endpoint**: `/register`
   - **Method**: `POST`
   - **Body**:
     ```json
     {
         "username": "your_username",
         "password": "your_password"
     }
     ```
   - **Response**: On successful registration, you will receive a confirmation message:
     ```json
     {
         "message": "User registered successfully"
     }
     ```

### Login to the API

After registration, you can log in to the API using the `/login` endpoint:

1. **Login to the API** using the `/login` endpoint with your username and password:
   - **Endpoint**: `/login`
   - **Method**: `POST`
   - **Body**:
     ```json
     {
         "username": "your_username",
         "password": "your_password"
     }
     ```
   - **Response**: On successful login, you will receive a token:
     ```json
     {
         "message": "Login successful",
         "token": "your_jwt_token"
     }
     ```

## API Authentication with Bearer Token

To access protected endpoints in the API, you need to include a Bearer token in the Authorization header of your requests. The protected endpoints include those for creating, updating, and deleting resources.

### Using the Bearer Token

Once you have the token, you can access protected routes by including it in the Authorization header of your requests.

#### Example of Protected Endpoint Requests

1. **Create an Item**
   - **Endpoint**: `/items`
   - **Method**: `POST`
   - **Headers**:
     - **Authorization**: `Bearer your_jwt_token`
   - **Body**:
     ```json
     {
         "name": "Item Name",
         "description": "Item Description",
         "price": 100,
         "category_id": 1
     }
     ```

2. **Update an Item**
   - **Endpoint**: `/items/{item_id}`
   - **Method**: `PUT`
   - **Headers**:
     - **Authorization**: `Bearer your_jwt_token`
   - **Body**:
     ```json
     {
         "name": "Updated Item Name",
         "description": "Updated Item Description",
         "price": 150,
         "category_id": 1
     }
     ```

3. **Delete an Item**
   - **Endpoint**: `/items/{item_id}`
   - **Method**: `DELETE`
   - **Headers**:
     - **Authorization**: `Bearer your_jwt_token`

### How to Set Up the Authorization Header in Postman

1. Open Postman and create a new request.
2. In the request tab, click on the **Headers** section.
3. Add a new header:
   - **Key**: `Authorization`
   - **Value**: `Bearer your_jwt_token`
4. Set the request type (e.g., POST, PUT, DELETE) and the endpoint URL (e.g., `http://localhost:8000/items` for creating or getting items).
5. If applicable, add the JSON body in the Body tab for POST and PUT requests.
6. Click **Send** to execute the request.
7. Example of this implementation can be downloaded here https://drive.google.com/file/d/1sS7kKSu3mg_In1NM8llruNhrR9GxscSJ/view?usp=sharing

**Debugging Process**

During the development of this application, several issues were encountered:

  * **JWT Token Issues:** The application returned a 500 error when the `SECRET_KEY` was not properly set in the environment. This was resolved by ensuring the key was loaded correctly from the `.env` file using `os.environ.get("SECRET_KEY")`.
  * **Password Hashing:** An error occurred when verifying the user's password against the stored hash. This was debugged by confirming that the password hashing mechanism was consistent when registering and logging in users.
  * **Database Connection Errors:** Connection errors were addressed by ensuring that the database file existed and was accessible.

**Assumptions and Decisions**

  * The application assumes a SQLite database will be used, making it easy to set up for local development.
  * User passwords are hashed using the `scrypt` algorithm for security.
  * JWT tokens are used for authentication, and their expiry is set to 3 hours for user sessions (currently this is hardcoded).
  * Validation and basic error handling is implemented, returning appropriate HTTP status codes and messages. 

**Future Improvements**

  * Implement unit tests using `pytest` to ensure the reliability of the application.
  * Add Docker implementation
  * Consider implementing pagination and filtering for item listings.

---

<p style="text-align: center;"><strong>Made with ❤️ by JonathanKevin</strong></p>

