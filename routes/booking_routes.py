from flask import Blueprint, request, jsonify, current_app, session
from datetime import datetime
from models import db, Booking, User

booking_bp = Blueprint('booking', __name__, url_prefix='/api')

def validate_booking_data(data):
    required_fields = ['equipment_id', 'date', 'hour', 'quantity', 'name', 'phone', 'email']
    errors = []
    for field in required_fields:
        if field not in data or data[field] in [None, ""]:
            errors.append(f"Поле {field} є обов’язковим.")
    try:
        qty = int(data.get('quantity', 0))
        if qty <= 0:
            errors.append("Кількість повинна бути більше 0.")
    except ValueError:
        errors.append("Кількість повинна бути числовою.")
    try:
        datetime.strptime(data.get('date', ''), "%Y-%m-%d")
    except ValueError:
        errors.append("Дата повинна бути у форматі YYYY-MM-DD.")
    # Проверка формата часа, ожидаем "HH:MM"
    if isinstance(data.get('hour'), str):
        try:
            datetime.strptime(data.get('hour'), "%H:%M")
        except ValueError:
            errors.append("Час повинен бути у форматі HH:MM (наприклад, 09:00).")
    else:
        try:
            h = int(data.get('hour'))
            if h < 0 or h > 23:
                errors.append("Час повинен бути між 0 та 23.")
        except ValueError:
            errors.append("Час повинен бути числовим або у форматі HH:MM.")
    return errors

@booking_bp.route('/book', methods=['POST'])
def create_booking():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Невірний JSON-запит."}), 400

    errors = validate_booking_data(data)
    if errors:
        return jsonify({"error": " ".join(errors)}), 400

    # Автоматическое создание учетной записи для гостей:
    # Если пользователь не залогинен, ищем по email; если не найден, создаем нового.
    user_id = session.get('user_id')
    if not user_id:
        email = data.get('email')
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            user_id = existing_user.id
        else:
            try:
                new_user = User(
                    name=data.get('name'),
                    phone=data.get('phone'),
                    email=email,
                    password='guest',  # Для гостей временный пароль
                    role='user'
                )
                db.session.add(new_user)
                db.session.commit()
                user_id = new_user.id
                session['user_id'] = user_id
            except Exception as e:
                current_app.logger.error(f"Помилка при створенні користувача: {e}")
                db.session.rollback()
                return jsonify({"error": "Помилка при створенні користувача."}), 500

    # Преобразование даты
    try:
        booking_date = datetime.strptime(data['date'], "%Y-%m-%d").date()
    except ValueError:
        return jsonify({"error": "Невірний формат дати. Використовуйте YYYY-MM-DD."}), 400

    # Преобразование времени: берем часы из строки "HH:MM"
    try:
        hour_str = data['hour']
        hour_int = int(hour_str.split(':')[0])
    except Exception as e:
        current_app.logger.error(f"Помилка при перетворенні часу: {e}")
        return jsonify({"error": "Невірний формат часу. Використовуйте формат HH:MM."}), 400

    try:
        new_booking = Booking(
            user_id=user_id,
            equipment_id=data['equipment_id'],
            date=booking_date,
            hour=hour_int,
            quantity=int(data['quantity']),
            comment=data.get('comment', "")
        )
        db.session.add(new_booking)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(f"Помилка при створенні бронювання: {e}")
        db.session.rollback()
        return jsonify({"error": "Виникла помилка на сервері під час створення бронювання."}), 500

    return jsonify({"message": "Бронювання підтверджено", "booking_id": new_booking.id}), 201

@booking_bp.route('/bookings', methods=['GET'])
def get_bookings():
    try:
        bookings = Booking.query.all()
        result = []
        for booking in bookings:
            result.append({
                "id": booking.id,
                "user_id": booking.user_id,
                "equipment_id": booking.equipment_id,
                "date": booking.date.strftime("%Y-%m-%d"),
                "hour": booking.hour,
                "quantity": booking.quantity,
                "comment": booking.comment
            })
    except Exception as e:
        current_app.logger.error(f"Помилка при отриманні бронювань: {e}")
        return jsonify({"error": "Виникла помилка на сервері під час отримання бронювань."}), 500

    return jsonify(result), 200
