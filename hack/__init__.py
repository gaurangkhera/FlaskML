import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

app =  Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

app.config['SECRET_KEY'] = 'secret'
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'+os.path.join(basedir,'data.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['STRIPE_PUBLISHABLE_KEY'] = 'pk_test_51MNXVzSJWkNpSKqnWP2poV24CZbd70xqJNtwhlIhDEM0tv2J5rNA07bSTd5FKwf9r0T0sRUONbRTL8JpjG6DS3ba008JFEaCy6'
app.config['STRIPE_SECRET_KEY'] = 'sk_test_51MNXVzSJWkNpSKqnQ2EPfRinu4486AOWVLrfABD4AYe9RAY2SOz9QWcEh3TGsKLVgLl3SEKV07I3tZBOeEVr8uDS00q61dOcRR'
db = SQLAlchemy(app)
Migrate(app,db)

def create_db(app):
    with app.app_context():
        db.create_all()