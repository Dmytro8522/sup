from extensions import db

# Пример базовых моделей
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.Text)  # если хочешь без ограничений
    phone = db.Column(db.String(20))
    role = db.Column(db.String(20), default='user')

class Equipment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(100))
    subcategory = db.Column(db.String(100))
    quantity = db.Column(db.Integer)
    price = db.Column(db.Float)

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', backref='bookings')
    date = db.Column(db.Date)
    hour = db.Column(db.Integer)
    items = db.relationship("BookingItem", backref="booking", lazy=True)

class BookingItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.Integer, db.ForeignKey('booking.id'))
    equipment_id = db.Column(db.Integer, db.ForeignKey('equipment.id'))
    quantity = db.Column(db.Integer, nullable=False)

    equipment = db.relationship('Equipment')

class Schedule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    day_of_week = db.Column(db.Integer)
    start_hour = db.Column(db.Integer)
    end_hour = db.Column(db.Integer)
