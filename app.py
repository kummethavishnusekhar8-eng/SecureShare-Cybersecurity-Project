from flask import Flask
from flask_login import LoginManager
from config import Config
from models import db, User
from flask_bcrypt import Bcrypt

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
bcrypt = Bcrypt(app)

login_manager = LoginManager()
login_manager.login_view = "login"
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

with app.app_context():
    db.create_all()
import os

os.makedirs("encrypted_files", exist_ok=True)
from auth import *

if __name__ == "__main__":
    app.run(debug=True)