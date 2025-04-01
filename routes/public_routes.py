from flask import Blueprint, jsonify
from models import Equipment

public_bp = Blueprint('public', __name__)

@public_bp.route("/equipment")
def public_equipment():
    equipment_list = Equipment.query.all()
    data = [{
        "id": eq.id,
        "category": eq.category,
        "subcategory": eq.subcategory,
        "quantity": eq.quantity,
        "price": eq.price
    } for eq in equipment_list]
    return jsonify(data)
