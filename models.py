from app import db
from datetime import datetime

class User(db.Model):
    __tablename__ = 'users'
    id       = db.Column(db.Integer, primary_key=True)
    name     = db.Column(db.String(100), nullable=False)
    phone    = db.Column(db.String(20), nullable=False)
    email    = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)  # хранить хеш пароля
    role     = db.Column(db.String(10), default='user')   # 'user' или 'admin'
    
    bookings = db.relationship('Booking', back_populates='user')

class Equipment(db.Model):
    __tablename__ = 'equipment'
    id          = db.Column(db.Integer, primary_key=True)
    category    = db.Column(db.String(50), nullable=False)    # Категория (Катамараны, САП-дошки, Каяки, Аутрігери)
    subcategory = db.Column(db.String(50), nullable=False)    # Подкатегория (напр., для САП-дошок: Спортивні, Туристичні, Дитячі)
    quantity    = db.Column(db.Integer, nullable=False)       # Общее количество единиц
    
    bookings   = db.relationship('Booking', back_populates='equipment')

class Booking(db.Model):
    __tablename__ = 'bookings'
    id           = db.Column(db.Integer, primary_key=True)
    user_id      = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    equipment_id = db.Column(db.Integer, db.ForeignKey('equipment.id'), nullable=False)
    date         = db.Column(db.Date, nullable=False)         # Дата бронирования
    hour         = db.Column(db.Integer, nullable=False)        # Час бронирования (с 9 до 20, например)
    quantity     = db.Column(db.Integer, nullable=False)        # Количество единиц
    comment      = db.Column(db.String(255), nullable=True)     # Комментарий или пожелание
    
    user      = db.relationship('User', back_populates='bookings')
    equipment = db.relationship('Equipment', back_populates='bookings')

class Schedule(db.Model):
    __tablename__ = 'schedule'
    id          = db.Column(db.Integer, primary_key=True)
    day_of_week = db.Column(db.Integer, nullable=False)   # 0 = понедельник ... 6 = воскресенье
    start_hour  = db.Column(db.Integer, nullable=False)   # время открытия (например, 9)
    end_hour    = db.Column(db.Integer, nullable=False)   # время закрытия (например, 20)
