from http.server import HTTPServer
from handlers import InventoryHandler
from models import init_db


def run(server_class=HTTPServer, handler_class=InventoryHandler, port=8000):
    init_db()  # Initialize database if not already set up
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f'Starting server on port {port}...')
    httpd.serve_forever()


if __name__ == '__main__':
    run()
