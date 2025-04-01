from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify, Response
from functools import wraps
from models import Equipment, BookingItem, Schedule, Booking, User
from flask import send_file
from datetime import datetime
from io import BytesIO
from extensions import db
import csv
import io

admin_bp = Blueprint('admin', __name__)

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if session.get('role') != 'admin':
            flash("У вас немає прав доступу до адмін-панелі", "danger")
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated

@admin_bp.route('/')
@admin_required
def admin_index():
    # Рендерим основную страницу адмін-панелі
    return render_template('admin_index.html')

@admin_bp.route('/equipment', methods=['GET'])
@admin_required
def admin_equipment():
    # Для AJAX-запроса возвращаем список оборудования в JSON
    equipment_list = Equipment.query.all()
    data = [{
        "id": eq.id,
        "category": eq.category,
        "subcategory": eq.subcategory,
        "quantity": eq.quantity,
        "price": eq.price
    } for eq in equipment_list]
    return jsonify(data)

@admin_bp.route('/equipment', methods=['POST'])
@admin_required
def add_equipment():
    # Добавление нового оборудования (принимается JSON)
    data = request.get_json()
    category = data.get('category')
    subcategory = data.get('subcategory')
    quantity = data.get('quantity')
    price = data.get('price')
    if not (category and subcategory and quantity is not None and price is not None):
        return jsonify({"error": "Будь ласка, заповніть усі поля"}), 400
    try:
        new_eq = Equipment(
            category=category,
            subcategory=subcategory,
            quantity=int(quantity),
            price=float(price)
        )
        db.session.add(new_eq)
        db.session.commit()
        return jsonify({"message": "Обладнання додано успішно!"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Сталася помилка при додаванні обладнання"}), 500

@admin_bp.route('/equipment/<int:eq_id>', methods=['PUT'])
@admin_required
def update_equipment(eq_id):
    # Редактирование оборудования (например, обновление количества, цены и т.д.)
    eq = Equipment.query.get_or_404(eq_id)
    data = request.get_json()
    if 'category' in data:
        eq.category = data['category']
    if 'subcategory' in data:
        eq.subcategory = data['subcategory']
    if 'quantity' in data:
        eq.quantity = int(data['quantity'])
    if 'price' in data:
        eq.price = float(data['price'])
    try:
        db.session.commit()
        return jsonify({"message": "Обладнання оновлено успішно!"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Сталася помилка при оновленні обладнання"}), 500

@admin_bp.route('/equipment/<int:eq_id>', methods=['DELETE'])
@admin_required
def delete_equipment(eq_id):
    eq = Equipment.query.get_or_404(eq_id)
    try:
        db.session.delete(eq)
        db.session.commit()
        return jsonify({"message": "Обладнання видалено!"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Сталася помилка при видаленні обладнання"}), 500

@admin_bp.route('/schedule', methods=['GET'])
@admin_required
def admin_schedule():
    # Для AJAX-запроса возвращаем расписание в JSON
    schedule_list = Schedule.query.all()
    data = [{
        "day_of_week": s.day_of_week,
        "start_hour": s.start_hour,
        "end_hour": s.end_hour
    } for s in schedule_list]
    return jsonify(data)

@admin_bp.route('/schedule', methods=['POST'])
@admin_required
def update_schedule():
    # Обновление расписания (принимается JSON)
    data = request.get_json()
    day_of_week = data.get('day_of_week')
    start_hour = data.get('start_hour')
    end_hour = data.get('end_hour')
    if day_of_week is None or start_hour is None or end_hour is None:
        return jsonify({"error": "Будь ласка, заповніть усі поля"}), 400
    try:
        day = int(day_of_week)
        start = int(start_hour)
        end = int(end_hour)
        schedule = Schedule.query.filter_by(day_of_week=day).first()
        if schedule:
            schedule.start_hour = start
            schedule.end_hour = end
        else:
            schedule = Schedule(day_of_week=day, start_hour=start, end_hour=end)
            db.session.add(schedule)
        db.session.commit()
        return jsonify({"message": "Розклад оновлено успішно!"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Сталася помилка при оновленні розкладу"}), 500


@admin_bp.route("/bookings", methods=["GET"])
@admin_required
def admin_bookings():
    bookings = Booking.query.order_by(Booking.date.desc()).all()
    data = []
    for booking in bookings:
        user = booking.user
        for item in booking.items:
            equipment = item.equipment
            data.append({
                "id": booking.id,
                "user": user.name if user else "—",
                "equipment": f"{equipment.category} – {equipment.subcategory}" if equipment else "—",
                "date": booking.date.strftime("%Y-%m-%d"),
                "time": f"{booking.hour}:00" if booking.hour else "—",
                "quantity": item.quantity,
                "total": item.total_price if hasattr(item, 'total_price') else (equipment.price * item.quantity if equipment else 0)
            })
    return jsonify(data)



@admin_bp.route('/export')
@admin_required
def export_bookings():
    output = BytesIO()
    writer = csv.writer(io.TextIOWrapper(output, encoding='utf-8', newline=''))

    writer.writerow(['Ім’я', 'Email', 'Телефон', 'Дата', 'Час', 'Категорія', 'Підкатегорія', 'Кількість'])

    bookings = Booking.query.all()

    for booking in bookings:
        user = booking.user
        for item in booking.items:
            equipment = item.equipment
            writer.writerow([
                user.name if user else "—",
                user.email if user else "—",
                user.phone if user else "—",
                booking.date.strftime('%Y-%m-%d') if booking.date else "—",
                f"{booking.hour}:00" if booking.hour is not None else "—",
                equipment.category if equipment else "—",
                equipment.subcategory if equipment else "—",
                item.quantity
            ])

    output.seek(0)

    return send_file(
        output,
        mimetype='text/csv',
        download_name=f'bookings_{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.csv',
        as_attachment=True
    )
