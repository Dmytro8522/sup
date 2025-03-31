from flask import Blueprint, request, redirect, url_for, flash, session
from models import db, Booking, Equipment
from datetime import datetime

booking_bp = Blueprint('booking', __name__, url_prefix='/booking')

@booking_bp.route('/create', methods=['POST'])
def create_booking():
    # Проверка, что пользователь авторизован
    if not session.get('user_id'):
        flash("Вам потрібно увійти", "danger")
        return redirect(url_for('auth.login'))
    
    user_id = session.get('user_id')
    equipment_id = request.form.get('equipment')
    date_str = request.form.get('date')
    time_str = request.form.get('time')
    quantity = request.form.get('quantity')
    
    # Валидация обязательных полей
    if not (equipment_id and date_str and time_str and quantity):
        flash("Будь ласка, заповніть усі поля", "danger")
        return redirect(url_for('dashboard.new_booking'))
    
    try:
        booking_date = datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        flash("Невірний формат дати", "danger")
        return redirect(url_for('dashboard.new_booking'))
    
    try:
        # Получаем час из строки, например, "15:30" -> 15
        booking_hour = int(time_str.split(":")[0])
    except Exception:
        flash("Невірний формат часу", "danger")
        return redirect(url_for('dashboard.new_booking'))
    
    try:
        quantity = int(quantity)
    except ValueError:
        flash("Невірна кількість", "danger")
        return redirect(url_for('dashboard.new_booking'))
    
    # Создаем новое бронирование
    new_booking = Booking(
        user_id=user_id,
        equipment_id=equipment_id,
        date=booking_date,
        hour=booking_hour,
        quantity=quantity
    )
    db.session.add(new_booking)
    db.session.commit()
    
    flash("Бронювання оформлено успішно!", "success")
    return redirect(url_for('dashboard.dashboard'))
