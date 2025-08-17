import datetime
import email
from . import db
import enum
import uuid



class User(db.Model):
    __tablename__ = "user"
    username = db.Column(db.String(80), primary_key=True)
    password = db.Column(db.String(80))
    email = db.Column(db.String(120), unique=True, nullable=False)
    money = db.Column(db.Float(), default=1000)
    token_status = db.Column(db.Boolean(), default=False)
    token = db.Column(db.String(290))

    def to_json(self):
        """Converts the User object to a JSON-serializable dictionary."""
        return {
            "username": self.username,
            "email": self.email,
            "money": self.money,
            "token_status": self.token_status,
            "token": self.token
        }

class BetType(enum.Enum):
    Monetary = 1
    Text = 2
    Other = 3

class BetStatus(enum.Enum):
    Pending = 1
    Accepted = 2
    Rejected = 3
    Win = 4
    Loss = 5

class Bets(db.Model):
    __tablename__ = "bets"
    uuid = db.Column(db.Uuid, primary_key=True, default=uuid.uuid4)
    u1 = db.Column(db.String(80))
    u2 = db.Column(db.String(80))
    type = db.Column(db.Enum(BetType))
    status = db.Column(db.Enum(BetStatus))
    coursecode = db.Column(db.String(80))
    year = db.Column(db.Integer())
    semester = db.Column(db.Integer())
    assessment = db.Column(db.String(80))
    upper = db.Column(db.Integer())
    lower = db.Column(db.Integer())
    wager1 = db.Column(db.Float())
    wager2 = db.Column(db.Float())
    description = db.Column(db.Text())

    def to_json(self):
        """Converts the Bets object to a JSON-serializable dictionary."""
        return {
            "uuid": str(self.uuid),
            "u1": self.u1,
            "u2": self.u2 if self.u2 else None,
            "type": self.type.name if self.type else None,
            "status": self.status.name if self.status else None,
            "coursecode": self.coursecode,
            "year": self.year,
            "semester": self.semester,
            "assessment": self.assessment,
            "upper": self.upper,
            "lower": self.lower,
            "wager1": self.wager1,
            "wager2": self.wager2,
            "description": self.description,
        }
    
class Courses(db.Model):
    __tablename__ = "courses"
    course_code = db.Column(db.String(80), primary_key=True)
    course_id = db.Column(db.String(80))
    course_name = db.Column(db.Text())
    
class AssignmentMap(db.Model):
    __tablename__ = "assignmentMap"
    uuid = db.Column(db.Uuid, primary_key=True, default=uuid.uuid4)
    ECP_name = db.Column(db.String(80))
    Grade_name = db.Column(db.String(80))
