import json
import sqlite3
import jwt
import os
import datetime
from dotenv import load_dotenv
from http.server import BaseHTTPRequestHandler
from models import Category, Item, User, connect_db

load_dotenv()
SECRET_KEY = os.getenv("SECRET")
# SECRET_KEY = os.environ.get("SECRET_KEY")


class InventoryHandler(BaseHTTPRequestHandler):

    def _set_headers(self, status_code=200):
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

    # Middleware for token authentication
    def _authenticate(self):
        token = self.headers.get('Authorization')
        if not token or not token.startswith("Bearer "):
            return False
        token = token.split(" ")[1]  # Get the token after "Bearer "
        try:
            jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            return True
        except jwt.ExpiredSignatureError:
            return False
        except jwt.InvalidTokenError:
            return False

    # Handling GET requests
    def do_GET(self):
        if self.path == '/categories':
            self._get_categories()
        elif self.path.startswith('/items'):
            item_id = self.path.split('/')[-1]
            if item_id.isdigit():
                self._get_item(int(item_id))
            else:
                self._get_items()
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({"error": "Not Found"}).encode())

    # Get all categories
    def _get_categories(self):
        try:
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Category")
            categories = cursor.fetchall()
            conn.close()

            self._set_headers(200)
            self.wfile.write(json.dumps([{"id": cat[0], "name": cat[1]} for cat in categories]).encode())
        except Exception as e:
            self._set_headers(500)
            self.wfile.write(json.dumps({"error": "Internal Server Error", "message": str(e)}).encode())

    # Get all items
    def _get_items(self):
        try:
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("""SELECT Item.id, Item.name, Item.description, Item.price, Category.name AS category_name 
                              FROM Item 
                              JOIN Category ON Item.category_id = Category.id""")
            items = cursor.fetchall()
            conn.close()

            items_list = [
                {
                    "id": item[0],
                    "name": item[1],
                    "description": item[2],
                    "price": item[3],
                    "category": item[4]
                }
                for item in items
            ]

            self._set_headers(200)
            self.wfile.write(json.dumps(items_list).encode())
        except Exception as e:
            self._set_headers(500)
            self.wfile.write(json.dumps({"error": "Internal Server Error", "message": str(e)}).encode())

    # Get a single item by ID
    def _get_item(self, item_id):
        try:
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("""SELECT Item.id, Item.name, Item.description, Item.price, Item.category_id, Category.name AS category_name
                              FROM Item
                              JOIN Category ON Item.category_id = Category.id
                              WHERE Item.id = ?""", (item_id,))
            item = cursor.fetchone()
            conn.close()

            if item:
                item_data = {
                    "id": item[0],
                    "name": item[1],
                    "description": item[2],
                    "price": item[3],
                    "category_id": item[4],
                    "category": item[5]
                }
                self._set_headers(200)
                self.wfile.write(json.dumps(item_data).encode())
            else:
                self._set_headers(404)
                self.wfile.write(json.dumps({"error": "Item not found"}).encode())
        except Exception as e:
            self._set_headers(500)
            self.wfile.write(json.dumps({"error": "Internal Server Error", "message": str(e)}).encode())

    # Handling POST requests
    def do_POST(self):
        if self.path == '/register':
            self._register_user()
        elif self.path == '/login':
            self._login_user()
        elif self.path == '/categories':
            if self._authenticate():
                self._create_category()
            else:
                self._set_headers(401)
                self.wfile.write(json.dumps({"error": "Unauthorized"}).encode())
        elif self.path == '/items':
            if self._authenticate():
                self._create_item()
            else:
                self._set_headers(401)
                self.wfile.write(json.dumps({"error": "Unauthorized"}).encode())
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({"error": "Not Found"}).encode())

    # Register a new user
    def _register_user(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        try:
            data = json.loads(post_data)
            if "username" in data and "password" in data:
                existing_user = User.find_by_username(data['username'])
                if existing_user:
                    self._set_headers(400)
                    self.wfile.write(json.dumps({"error": "Username already exists"}).encode())
                else:
                    user = User(data['username'], data['password'])
                    user.save()
                    self._set_headers(201)
                    self.wfile.write(json.dumps({"message": "User registered successfully"}).encode())
            else:
                self._set_headers(400)
                self.wfile.write(json.dumps({"error": "Invalid data, 'username' and 'password' are required"}).encode())
        except json.JSONDecodeError:
            self._set_headers(400)
            self.wfile.write(json.dumps({"error": "Invalid JSON data"}).encode())
        except Exception as e:
            self._set_headers(500)
            self.wfile.write(json.dumps({"error": "Internal Server Error", "message": str(e)}).encode())

    # Login a user and issue a token
    def _login_user(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        try:
            data = json.loads(post_data)
            if "username" in data and "password" in data:
                user = User.find_by_username(data['username'])
                print(os.environ.get("SECRET_KEY", "your_secret_key_here"))
                if user and User.check_password(user[2], data['password']):
                    expiration_time = datetime.datetime.utcnow() + datetime.timedelta(hours=3)
                    token = jwt.encode({'username': user[1], 'exp': expiration_time}, SECRET_KEY, algorithm='HS256')
                    self._set_headers(200)
                    self.wfile.write(json.dumps({"message": "Login successful", "token": token}).encode())
                else:
                    self._set_headers(400)
                    self.wfile.write(json.dumps({"error": "Invalid username or password"}).encode())
            else:
                self._set_headers(400)
                self.wfile.write(json.dumps({"error": "Invalid data, 'username' and 'password' are required"}).encode())
        except json.JSONDecodeError:
            self._set_headers(400)
            self.wfile.write(json.dumps({"error": "Invalid JSON data"}).encode())
        except Exception as e:
            self._set_headers(500)
            self.wfile.write(json.dumps({"error": "Internal Server Error", "message": str(e)}).encode())

    # Create a new category
    def _create_category(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        try:
            data = json.loads(post_data)
            if "name" in data and isinstance(data["name"], str) and data["name"].strip():
                category = Category(data['name'])
                category.save()
                self._set_headers(201)
                self.wfile.write(json.dumps({"message": "Category created successfully"}).encode())
            else:
                self._set_headers(400)
                self.wfile.write(
                    json.dumps({"error": "Invalid data, 'name' is required and must be a non-empty string"}).encode())
        except sqlite3.IntegrityError:
            self._set_headers(400)
            self.wfile.write(json.dumps({"error": "Category already exists"}).encode())
        except Exception as e:
            self._set_headers(500)
            self.wfile.write(json.dumps({"error": "Internal Server Error", "message": str(e)}).encode())

    # Create a new item
    def _create_item(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        try:
            data = json.loads(post_data)
            if (
                    "category_id" in data and isinstance(data["category_id"], int) and
                    "name" in data and isinstance(data["name"], str) and data["name"].strip() and
                    "price" in data and isinstance(data["price"], (int, float))
            ):
                item = Item(data['category_id'], data['name'], data.get('description', ''), data['price'])
                item.save()
                self._set_headers(201)
                self.wfile.write(json.dumps({"message": "Item created successfully"}).encode())
            else:
                self._set_headers(400)
                self.wfile.write(json.dumps({
                    "error": "Invalid data, 'category_id' (int), 'name' (non-empty string), and 'price' (number) are required"
                }).encode())
        except sqlite3.IntegrityError:
            self._set_headers(400)
            self.wfile.write(json.dumps({"error": "Category ID does not exist"}).encode())
        except Exception as e:
            self._set_headers(500)
            self.wfile.write(json.dumps({"error": "Internal Server Error", "message": str(e)}).encode())

    # Handling PUT requests
    def do_PUT(self):
        if not self._authenticate():
            self._set_headers(401)
            self.wfile.write(json.dumps({"error": "Unauthorized"}).encode())
            return

        item_id = self.path.split('/')[-1]
        if item_id.isdigit():
            content_length = int(self.headers['Content-Length'])
            put_data = self.rfile.read(content_length)
            try:
                data = json.loads(put_data)
                self._update_item(int(item_id), data)
            except json.JSONDecodeError:
                self._set_headers(400)
                self.wfile.write(json.dumps({"error": "Invalid JSON data"}).encode())
            except Exception as e:
                self._set_headers(500)
                self.wfile.write(json.dumps({"error": "Internal Server Error", "message": str(e)}).encode())
        else:
            self._set_headers(400)
            self.wfile.write(json.dumps({"error": "Invalid item ID"}).encode())

    # Update an item
    def _update_item(self, item_id, data):
        try:
            conn = connect_db()
            cursor = conn.cursor()
            fields = []
            params = []

            # Collect fields and parameters for the update query
            if "name" in data:
                fields.append("name = ?")
                params.append(data["name"])
            if "description" in data:
                fields.append("description = ?")
                params.append(data["description"])
            if "price" in data:
                fields.append("price = ?")
                params.append(data["price"])
            if "category_id" in data:
                fields.append("category_id = ?")
                params.append(data["category_id"])

            # Only proceed if there are fields to update
            if fields:
                params.append(item_id)  # Append item_id at the end
                cursor.execute(f"UPDATE Item SET {', '.join(fields)} WHERE id = ?", params)
                conn.commit()

                if cursor.rowcount:
                    # Successful update, return 200 OK with a success message
                    self._set_headers(200)
                    self.wfile.write(json.dumps({"message": "Item updated successfully"}).encode())
                else:
                    # If no rows were updated, the item was not found
                    self._set_headers(404)
                    self.wfile.write(json.dumps({"error": "Item not found"}).encode())
            else:
                # If no fields to update, return a bad request
                self._set_headers(400)
                self.wfile.write(json.dumps({"error": "No fields to update"}).encode())
        except sqlite3.IntegrityError:
            self._set_headers(400)
            self.wfile.write(json.dumps({"error": "Invalid category ID"}).encode())
        except Exception as e:
            self._set_headers(500)
            self.wfile.write(json.dumps({"error": "Internal Server Error", "message": str(e)}).encode())
        finally:
            conn.close()  # Ensure the connection is closed even if there's an error

    # Handling DELETE requests
    def do_DELETE(self):
        if not self._authenticate():
            self._set_headers(401)
            self.wfile.write(json.dumps({"error": "Unauthorized"}).encode())
            return

        item_id = self.path.split('/')[-1]
        if item_id.isdigit():
            self._delete_item(int(item_id))
        else:
            self._set_headers(400)
            self.wfile.write(json.dumps({"error": "Invalid item ID"}).encode())

    # Delete an item
    def _delete_item(self, item_id):
        try:
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM Item WHERE id = ?", (item_id,))
            # Check if any row was deleted
            if cursor.rowcount > 0:
                conn.commit()
                conn.close()
                self._set_headers(200)  # Change to 200 OK for successful deletion
                self.wfile.write(json.dumps({"message": "Item deleted successfully"}).encode())
            else:
                conn.close()
                self._set_headers(404)  # Not Found if no rows were affected
                self.wfile.write(json.dumps({"error": "Item not found"}).encode())
        except Exception as e:
            self._set_headers(500)
            self.wfile.write(json.dumps({"error": "Internal Server Error", "message": str(e)}).encode())
