import datetime
import email
from . import db
import enum



class User(db.Model):
    __tablename__ = "user"
    username = db.Column(db.String(80), primary_key=True)
    password = db.Column(db.String(80))
    email = db.Column(db.String(120), unique=True, nullable=False)

class BetType(enum.Enum):
    Monetary = 1
    Text = 2
    Other = 3

class BetStatus(enum.Enum):
    Pending = 1
    Accepted = 2
    Rejected = 3
    Completed = 4

class Bets(db.Model):
    __tablename__ = "bets"
    uuid = db.Column(db.String(80), primary_key=True)
    u1 = db.Column(db.String(80))
    u2 = db.Column(db.String(80))
    type = db.Column(db.Enum(BetType))
    status = db.Column(db.Enum(BetStatus))
    upper = db.Column(db.Integer())
    lower = db.Column(db.Integer())
    wager1 = db.Column(db.Float())
    wager2 = db.Column(db.Float())
    description = db.Column(db.Text())