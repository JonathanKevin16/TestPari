from http.server import HTTPServer
from handlers import InventoryHandler
from models import init_db
import sqlite3


def run(server_class=HTTPServer, handler_class=InventoryHandler, port=8000):
    try:
        init_db()

        # Start server
        server_address = ('', port)
        httpd = server_class(server_address, handler_class)
        print(f"Starting server on port {port}...")
        httpd.serve_forever()

    except sqlite3.Error as e:
        print(f"Error: Could not connect to the database. {e}")

    except Exception as e:
        print(f"Server error: {e}")

    finally:
        print("Server has been shut down.")


if __name__ == '__main__':
    run()
