"""WSGI entry point for production deployment."""
from src.app import create_app
import os

app = create_app(config_name=os.environ.get('FLASK_ENV', 'production'))

if __name__ == '__main__':
    app.run()

