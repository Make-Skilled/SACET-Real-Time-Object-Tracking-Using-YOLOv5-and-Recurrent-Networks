from flask import Flask, render_template, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_cors import CORS
import os

app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SESSION_TYPE'] = 'filesystem'  # Use filesystem-based sessions
app.config['UPLOAD_FOLDER'] = 'uploads'  # Folder to store uploaded images

# Create upload folder if it doesn't exist
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# Initialize extensions
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
CORS(app)  # Allow frontend requests

# Import Routes (Keep it after initializing db)
from routes import *

# Create database tables inside app context
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True,port=9001)
