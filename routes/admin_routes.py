from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify, Response
from functools import wraps
from models import Equipment, Schedule, Booking, User
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

@admin_bp.route('/bookings', methods=['GET'])
@admin_required
def admin_bookings():
    # Для AJAX-запроса возвращаем список бронювань в JSON
    bookings = Booking.query.order_by(Booking.date.desc()).all()
    data = []
    for b in bookings:
        data.append({
            "id": b.id,
            "user_id": b.user.id if b.user else None,
            "equipment_id": b.equipment.id if b.equipment else None,
            "date": b.date.strftime("%Y-%m-%d"),
            "hour": b.hour,
            "quantity": b.quantity,
            "comment": b.comment or ""
        })
    return jsonify(data)

@admin_bp.route('/export', methods=['GET'])
@admin_required
def export_bookings():
    bookings = Booking.query.order_by(Booking.date.desc()).all()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
    b.id,
    b.user.name if b.user else "",
    f"{b.equipment.category} – {b.equipment.subcategory}" if b.equipment else "",
    b.date.strftime("%Y-%m-%d"),
    f"{b.hour}:00",
    b.quantity,
    b.equipment.price * b.quantity if b.equipment else 0
])
    output.seek(0)
    return Response(output.getvalue(), mimetype='text/csv',
                    headers={"Content-Disposition": "attachment;filename=bookings.csv"})
