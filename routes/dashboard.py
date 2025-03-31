from flask import Blueprint, render_template, session, redirect, url_for
from models import User, Booking, Equipment
from app import db

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/dashboard')
def dashboard():
    if not session.get('user_id'):
        return redirect(url_for('auth.login'))
    user = User.query.get(session.get('user_id'))
    bookings = Booking.query.filter_by(user_id=user.id).all()
    return render_template('dashboard.html', bookings=bookings)

@dashboard_bp.route('/new_booking')
def new_booking():
    if not session.get('user_id'):
        return redirect(url_for('auth.login'))
    user = User.query.get(session.get('user_id'))
    # Получаем список оборудования для выбора
    equipment_list = Equipment.query.all()
    return render_template('booking_form.html', user=user, equipment_list=equipment_list)
