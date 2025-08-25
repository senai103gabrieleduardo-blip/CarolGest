import os
import logging
from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix

try:
    from flask_login import LoginManager
except ImportError:
    print("flask_login not found, installing...")
    import subprocess
    subprocess.check_call(["pip", "install", "flask-login"])
    from flask_login import LoginManager

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'  # type: ignore
login_manager.login_message = 'Por favor, faça login para acessar esta página.'

# Import models and routes after app creation to avoid circular imports
from models import User, Client, KanbanCard, WhatsAppMessage, SocialAccount, SocialPost
from routes import *

@login_manager.user_loader
def load_user(user_id):
    return User.get(int(user_id))

# Initialize sample data
def init_sample_data():
    # Create admin user if not exists
    if not User.get_by_username('admin'):
        admin = User(
            username='admin',
            email='admin@monteirocorretora.com',
            name='Administrador',
            role='admin'
        )
        admin.set_password('admin123')
        User.save(admin)
    
    # Create sample sales user
    if not User.get_by_username('vendedor1'):
        sales_user = User(
            username='vendedor1',
            email='vendedor@monteirocorretora.com',
            name='João Vendedor',
            role='sales'
        )
        sales_user.set_password('vendedor123')
        User.save(sales_user)

# Initialize data on startup
init_sample_data()
