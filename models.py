from extensions import db
from datetime import datetime

class User(db.Model):
    __tablename__ = 'users'
    id       = db.Column(db.Integer, primary_key=True)
    name     = db.Column(db.String(100), nullable=False)
    phone    = db.Column(db.String(20), nullable=False)
    email    = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    role     = db.Column(db.String(10), default='user')
    
    bookings = db.relationship('Booking', back_populates='user')

class Equipment(db.Model):
    __tablename__ = 'equipment'
    id          = db.Column(db.Integer, primary_key=True)
    category    = db.Column(db.String(50), nullable=False)
    subcategory = db.Column(db.String(50), nullable=False)
    quantity    = db.Column(db.Integer, nullable=False)
    price       = db.Column(db.Float, nullable=False, default=0.0)
    
    bookings   = db.relationship('Booking', back_populates='equipment')

class Booking(db.Model):
    __tablename__ = 'bookings'
    id           = db.Column(db.Integer, primary_key=True)
    user_id      = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    equipment_id = db.Column(db.Integer, db.ForeignKey('equipment.id'), nullable=False)
    date         = db.Column(db.Date, nullable=False)
    hour         = db.Column(db.Integer, nullable=False)
    quantity     = db.Column(db.Integer, nullable=False)
    comment      = db.Column(db.String(255), nullable=True)
    
    user      = db.relationship('User', back_populates='bookings')
    equipment = db.relationship('Equipment', back_populates='bookings')

class Schedule(db.Model):
    __tablename__ = 'schedule'
    id          = db.Column(db.Integer, primary_key=True)
    day_of_week = db.Column(db.Integer, nullable=False)
    start_hour  = db.Column(db.Integer, nullable=False)
    end_hour    = db.Column(db.Integer, nullable=False)
