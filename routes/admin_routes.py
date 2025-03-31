from flask import Blueprint, request, jsonify, current_app
from models import db, Equipment, Schedule, Booking, User
import csv, io

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# --- Equipment CRUD ---
@admin_bp.route('/equipment', methods=['GET'])
def get_equipment():
    try:
        equipment_list = Equipment.query.all()
        result = []
        for eq in equipment_list:
            result.append({
                "id": eq.id,
                "category": eq.category,
                "subcategory": eq.subcategory,
                "quantity": eq.quantity
            })
    except Exception as e:
        current_app.logger.error(f"Error fetching equipment: {e}")
        return jsonify({"error": "Server error fetching equipment."}), 500
    return jsonify(result), 200

@admin_bp.route('/equipment', methods=['POST'])
def add_equipment():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid JSON."}), 400
    try:
        # Ожидаем поля: category, subcategory, quantity
        category = data.get('category')
        subcategory = data.get('subcategory')
        quantity = int(data.get('quantity'))
        if not (category and subcategory and quantity):
            return jsonify({"error": "Missing fields."}), 400
        new_eq = Equipment(category=category, subcategory=subcategory, quantity=quantity)
        db.session.add(new_eq)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(f"Error adding equipment: {e}")
        db.session.rollback()
        return jsonify({"error": "Error adding equipment."}), 500
    return jsonify({"message": "Equipment added", "id": new_eq.id}), 201

@admin_bp.route('/equipment/<int:eq_id>', methods=['PUT'])
def update_equipment(eq_id):
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid JSON."}), 400
    try:
        eq = Equipment.query.get_or_404(eq_id)
        if 'category' in data:
            eq.category = data['category']
        if 'subcategory' in data:
            eq.subcategory = data['subcategory']
        if 'quantity' in data:
            eq.quantity = int(data['quantity'])
        db.session.commit()
    except Exception as e:
        current_app.logger.error(f"Error updating equipment: {e}")
        db.session.rollback()
        return jsonify({"error": "Error updating equipment."}), 500
    return jsonify({"message": "Equipment updated"}), 200

@admin_bp.route('/equipment/<int:eq_id>', methods=['DELETE'])
def delete_equipment(eq_id):
    try:
        eq = Equipment.query.get_or_404(eq_id)
        db.session.delete(eq)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(f"Error deleting equipment: {e}")
        db.session.rollback()
        return jsonify({"error": "Error deleting equipment."}), 500
    return jsonify({"message": "Equipment deleted"}), 200

# --- Schedule CRUD ---
@admin_bp.route('/schedule', methods=['GET'])
def get_schedule():
    try:
        schedule_list = Schedule.query.all()
        result = []
        for sch in schedule_list:
            result.append({
                "id": sch.id,
                "day_of_week": sch.day_of_week,
                "start_hour": sch.start_hour,
                "end_hour": sch.end_hour
            })
    except Exception as e:
        current_app.logger.error(f"Error fetching schedule: {e}")
        return jsonify({"error": "Server error fetching schedule."}), 500
    return jsonify(result), 200

@admin_bp.route('/schedule', methods=['POST'])
def set_schedule():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid JSON."}), 400
    try:
        day = int(data.get('day_of_week'))
        start = int(data.get('start_hour'))
        end = int(data.get('end_hour'))
        if start >= end:
            return jsonify({"error": "Start hour must be less than end hour."}), 400
        sch = Schedule.query.filter_by(day_of_week=day).first()
        if sch:
            sch.start_hour = start
            sch.end_hour = end
        else:
            sch = Schedule(day_of_week=day, start_hour=start, end_hour=end)
            db.session.add(sch)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(f"Error setting schedule: {e}")
        db.session.rollback()
        return jsonify({"error": "Error setting schedule."}), 500
    return jsonify({"message": f"Schedule updated for day {day}."}), 200

# --- Bookings ---
@admin_bp.route('/bookings', methods=['GET'])
def get_admin_bookings():
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
        current_app.logger.error(f"Error fetching bookings: {e}")
        return jsonify({"error": "Server error fetching bookings."}), 500
    return jsonify(result), 200

# --- Export ---
@admin_bp.route('/export', methods=['GET'])
def export_bookings():
    try:
        bookings = Booking.query.all()
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['ID', 'User ID', 'Equipment ID', 'Date', 'Hour', 'Quantity', 'Comment'])
        for booking in bookings:
            writer.writerow([
                booking.id,
                booking.user_id,
                booking.equipment_id,
                booking.date.strftime("%Y-%m-%d"),
                booking.hour,
                booking.quantity,
                booking.comment or ""
            ])
        output.seek(0)
        return output.getvalue(), 200, {
            "Content-Type": "text/csv; charset=utf-8",
            "Content-Disposition": "attachment; filename=bookings.csv"
        }
    except Exception as e:
        current_app.logger.error(f"Error exporting bookings: {e}")
        return jsonify({"error": "Error exporting bookings."}), 500
