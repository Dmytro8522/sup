from flask import Blueprint, request, jsonify
from extensions import db
from models import Booking, BookingItem, User, Equipment
from datetime import datetime

api_bp = Blueprint('api', __name__)

@api_bp.route('/api/book', methods=['POST'])
def book():
    data = request.get_json()
    name = data.get('name')
    phone = data.get('phone')
    email = data.get('email')
    date_str = data.get('date')
    hour_str = data.get('hour')  # пример: '9:00'
    hour = int(hour_str.split(':')[0])

    items = data.get('items', [])

    if not all([name, phone, email, date_str, hour, items]):
        return jsonify({"error": "Будь ласка, заповніть усі поля"}), 400

    try:
        booking_date = datetime.strptime(date_str, "%Y-%m-%d").date()

        # Создаём или находим пользователя
        user = User.query.filter_by(email=email).first()
        if not user:
            user = User(name=name, email=email)
            db.session.add(user)
            db.session.flush()  # получаем user.id

        # Создаём бронирование
        booking = Booking(user_id=user.id, date=booking_date, hour=hour)
        db.session.add(booking)
        db.session.flush()  # получаем booking.id

        for item in items:
            equipment_id = int(item["equipment_id"])
            qty = int(item["quantity"])
            booking_item = BookingItem(
                booking_id=booking.id,
                equipment_id=equipment_id,
                quantity=qty
            )
            db.session.add(booking_item)

        db.session.commit()
        return jsonify({"booking_id": booking.id})

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Помилка при збереженні бронювання"}), 500
