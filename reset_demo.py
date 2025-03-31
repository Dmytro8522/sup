from extensions import db
from models import User, Booking, Equipment, Schedule
from app import app

# Укажи здесь ID администратора, которого нужно оставить
ADMIN_ID = 1

with app.app_context():
    print("Очистка базы данных...")

    User.query.filter(User.id != ADMIN_ID).delete()
    Booking.query.delete()
    Equipment.query.delete()
    Schedule.query.delete()
    db.session.commit()

    print("Готово. Все данные удалены, кроме администратора.")
