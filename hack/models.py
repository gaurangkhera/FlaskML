from hack import db,login_manager
from werkzeug.security import generate_password_hash,check_password_hash
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

class User(db.Model,UserMixin):
    id = db.Column(db.Integer,primary_key = True)
    username = db.Column(db.String, nullable=False)
    email = db.Column(db.String(64),index=True)
    password = db.Column(db.String)
    membership = db.Column(db.String, default='Free')
    sep = db.Column(db.String)
    csvs = db.relationship('CSVFile', backref='user', lazy='joined')

class CSVFile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    path = db.Column(db.String, nullable=False)
    uploader = db.Column(db.String, db.ForeignKey('user.username'))