from flask import Blueprint, request, jsonify
from extensions import db
from models import Equipment, Booking, Schedule, BookingItem
from datetime import datetime, timedelta

availability_bp = Blueprint('availability', __name__)

@availability_bp.route('/api/availability', methods=['GET'])
def check_availability():
    date_str = request.args.get('date')
    today = datetime.today().date()
    now_hour = datetime.now().hour

    # Список всех дат с рабочим расписанием (начиная с сегодня)
    future_days = []
    for i in range(0, 14):  # проверяем 14 дней вперёд
        day = today + timedelta(days=i)
        weekday = day.weekday()
        schedule = Schedule.query.filter_by(day_of_week=weekday).first()
        if schedule:
            future_days.append(day.strftime("%Y-%m-%d"))

    if not date_str:
        return jsonify({"dates": future_days, "hours": []})

    try:
        date = datetime.strptime(date_str, "%Y-%m-%d").date()
        weekday = date.weekday()
        schedule = Schedule.query.filter_by(day_of_week=weekday).first()
        if not schedule:
            return jsonify({"dates": future_days, "hours": []})

        start = schedule.start_hour
        end = schedule.end_hour

        available_hours = []
        for hour in range(start, end):
            if date == today and hour <= now_hour:
                continue  # не показываем прошедшее время сегодня

            bookings = Booking.query.filter_by(date=date, hour=hour).all()

            equipment_counts = {}
            for booking in bookings:
                for item in booking.items:
                    key = item.equipment_id
                    equipment_counts[key] = equipment_counts.get(key, 0) + item.quantity

            all_equipment = Equipment.query.all()
            available = False
            for eq in all_equipment:
                booked = equipment_counts.get(eq.id, 0)
                if booked < eq.quantity:
                    available = True
                    break

            if available:
                available_hours.append(f"{hour}:00")

        return jsonify({"dates": future_days, "hours": available_hours})

    except:
        return jsonify({"dates": future_days, "hours": []})
