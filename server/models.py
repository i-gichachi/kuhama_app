from flask_sqlalchemy import SQLAlchemy
from sqlalchemy_serializer import SerializerMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class User(db.Model, SerializerMixin):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    second_name = db.Column(db.String(50))
    surname = db.Column(db.String(50), nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    phone_number = db.Column(db.String(9), unique=True, nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    location = db.Column(db.String(100))
    date_of_birth = db.Column(db.Date)
    password_hash = db.Column(db.String(255))
    user_type = db.Column(db.String(50), default='customer')

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

# Inventory Model
class Inventory(db.Model, SerializerMixin):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    item_name = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Integer, default=1)
    description = db.Column(db.Text, nullable=True)
    category = db.Column(db.String(50), nullable=True)
    condition = db.Column(db.String(50), nullable=True) 

# MovingDetail Model
class MovingDetail(db.Model, SerializerMixin):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    from_location = db.Column(db.String(100), nullable=False) 
    to_location = db.Column(db.String(100), nullable=False)    
    from_lat = db.Column(db.Float, nullable=False)  
    from_lon = db.Column(db.Float, nullable=False)  
    to_lat = db.Column(db.Float, nullable=False)    
    to_lon = db.Column(db.Float, nullable=False)   
    home_size = db.Column(db.String(50), nullable=False)
    moving_date = db.Column(db.DateTime, nullable=False)
    price = db.Column(db.Float, nullable=False)
    packing_service = db.Column(db.Boolean, default=False)  
    additional_details = db.Column(db.Text)
    status = db.Column(db.String(50), nullable=False, default='pending')


class Notification(db.Model, SerializerMixin):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    message = db.Column(db.String(255))
    read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Message(db.Model, SerializerMixin):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    content = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
