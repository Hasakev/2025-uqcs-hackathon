import datetime
import email
from . import db

class User(db.Model):
    __tablename__ = "user"
    username = db.Column(db.String(80), primary_key=True)
    password = db.Column(db.String(80))
    email = db.Column(db.String(120), unique=True, nullable=False)