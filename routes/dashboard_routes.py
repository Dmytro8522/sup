from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from datetime import datetime
from models import Booking, Equipment, Schedule
from app import db

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')

@dashboard_bp.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    user_id = session['user_id']
    bookings = Booking.query.filter_by(user_id=user_id).all()
    schedule_entries = Schedule.query.all()
    schedule = [{"day_of_week": sch.day_of_week, "start_hour": sch.start_hour, "end_hour": sch.end_hour} for sch in schedule_entries]
    return render_template('dashboard.html', bookings=bookings, schedule=schedule)

@dashboard_bp.route('/new_booking', methods=['GET', 'POST'])
def new_booking():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    if request.method == 'GET':
        return redirect(url_for('dashboard.dashboard_home'))
    category = request.form.get('category')
    subcategory = request.form.get('subcategory')
    quantity = request.form.get('quantity', type=int)
    date_str = request.form.get('date')
    hour = request.form.get('hour', type=int)
    comment = ""
    if not category or not subcategory or not date_str or hour is None or quantity is None:
        flash("Будь ласка, заповніть всі обов'язкові поля форми.", "danger")
        return redirect(url_for('dashboard.dashboard_home'))
    try:
        booking_date = datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        flash("Неправильний формат дати.", "danger")
        return redirect(url_for('dashboard.dashboard_home'))
    equipment = Equipment.query.filter_by(category=category, subcategory=subcategory).first()
    if equipment is None:
        flash("Обране спорядження не знайдено.", "warning")
        return redirect(url_for('dashboard.dashboard_home'))
    new_booking = Booking(user_id=session['user_id'],
                          equipment_id=equipment.id,
                          date=booking_date,
                          hour=hour,
                          quantity=quantity,
                          comment=comment)
    db.session.add(new_booking)
    db.session.commit()
    flash("Бронювання успішно створено!", "success")
    return redirect(url_for('dashboard.dashboard_home'))
