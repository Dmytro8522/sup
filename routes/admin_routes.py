from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from functools import wraps
from models import Equipment, Schedule, Booking
from extensions import db

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
    # Основная страница админ-панели
    return render_template('admin_index.html')

@admin_bp.route('/equipment')
@admin_required
def admin_equipment():
    equipment_list = Equipment.query.all()
    return render_template('admin_equipment.html', equipment=equipment_list)

@admin_bp.route('/bookings')
@admin_required
def admin_bookings():
    bookings = Booking.query.order_by(Booking.date.desc()).all()
    return render_template('admin_bookings.html', bookings=bookings)

@admin_bp.route('/add_equipment', methods=['POST'])
@admin_required
def add_equipment():
    category = request.form.get('category')
    subcategory = request.form.get('subcategory')
    quantity = request.form.get('quantity')
    price = request.form.get('price')
    if not (category and subcategory and quantity and price):
        flash("Будь ласка, заповніть усі поля", "danger")
        return redirect(url_for('admin.admin_index'))
    try:
        new_eq = Equipment(
            category=category,
            subcategory=subcategory,
            quantity=int(quantity),
            price=float(price)
        )
        db.session.add(new_eq)
        db.session.commit()
        flash("Обладнання додано успішно!", "success")
    except Exception as e:
        db.session.rollback()
        flash("Сталася помилка при додаванні обладнання", "danger")
    return redirect(url_for('admin.admin_equipment'))

@admin_bp.route('/update_schedule', methods=['POST'])
@admin_required
def update_schedule():
    day_of_week = request.form.get('day_of_week')
    start_hour = request.form.get('start_hour')
    end_hour = request.form.get('end_hour')
    if not (day_of_week and start_hour and end_hour):
        flash("Будь ласка, заповніть усі поля", "danger")
        return redirect(url_for('admin.admin_index'))
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
        flash("Розклад оновлено успішно!", "success")
    except Exception as e:
        db.session.rollback()
        flash("Сталася помилка при оновленні розкладу", "danger")
    return redirect(url_for('admin.admin_index'))
