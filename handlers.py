import json
import sqlite3
from http.server import BaseHTTPRequestHandler
from models import Category, Item, User, connect_db


class InventoryHandler(BaseHTTPRequestHandler):

    def _set_headers(self, status_code=200):
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

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
            cursor.execute("""SELECT Item.id, Item.name, Item.description, Item.price, Category.name AS category_name
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
                    "category": item[4]
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
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)

        try:
            data = json.loads(post_data)
            if self.path == '/register':
                self._register_user(data)
            elif self.path == '/login':
                self._login_user(data)
            elif self.path == '/categories':
                self._create_category(data)
            elif self.path == '/items':
                self._create_item(data)
            else:
                self._set_headers(404)
                self.wfile.write(json.dumps({"error": "Not Found"}).encode())
        except json.JSONDecodeError:
            self._set_headers(400)
            self.wfile.write(json.dumps({"error": "Invalid JSON data"}).encode())
        except Exception as e:
            self._set_headers(500)
            self.wfile.write(json.dumps({"error": "Internal Server Error", "message": str(e)}).encode())

    # Register a new user
    def _register_user(self, data):
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

    # Login a user
    def _login_user(self, data):
        if "username" in data and "password" in data:
            user = User.find_by_username(data['username'])
            if user and User.check_password(user[2], data['password']):
                self._set_headers(200)
                self.wfile.write(json.dumps({"message": "Login successful"}).encode())
            else:
                self._set_headers(400)
                self.wfile.write(json.dumps({"error": "Invalid username or password"}).encode())
        else:
            self._set_headers(400)
            self.wfile.write(json.dumps({"error": "Invalid data, 'username' and 'password' are required"}).encode())

    # Create a new category
    def _create_category(self, data):
        try:
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
    def _create_item(self, data):
        try:
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
                                                "error": "Invalid data, 'category_id' (int), 'name' (non-empty string), and 'price' (number) are required"}).encode())
        except sqlite3.IntegrityError:
            self._set_headers(400)
            self.wfile.write(json.dumps({"error": "Foreign key constraint failed"}).encode())
        except Exception as e:
            self._set_headers(500)
            self.wfile.write(json.dumps({"error": "Internal Server Error", "message": str(e)}).encode())

    # Handling PUT requests (for updating items)
    def do_PUT(self):
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
            cursor.execute("""UPDATE Item
                              SET name = ?, description = ?, price = ?, category_id = ?
                              WHERE id = ?""",
                           (data.get('name'), data.get('description', ''), data.get('price'), data.get('category_id'),
                            item_id))
            conn.commit()

            if cursor.rowcount:
                self._set_headers(200)
                self.wfile.write(json.dumps({"message": "Item updated successfully"}).encode())
            else:
                self._set_headers(404)
                self.wfile.write(json.dumps({"error": "Item not found"}).encode())
        except Exception as e:
            self._set_headers(500)
            self.wfile.write(json.dumps({"error": "Internal Server Error", "message": str(e)}).encode())
        finally:
            conn.close()

    # Handling DELETE requests
    def do_DELETE(self):
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
            conn.commit()

            if cursor.rowcount:
                self._set_headers(200)
                self.wfile.write(json.dumps({"message": "Item deleted successfully"}).encode())
            else:
                self._set_headers(404)
                self.wfile.write(json.dumps({"error": "Item not found"}).encode())
        except Exception as e:
            self._set_headers(500)
            self.wfile.write(json.dumps({"error": "Internal Server Error", "message": str(e)}).encode())
        finally:
            conn.close()
