from app import app, db
from models import User
from werkzeug.security import generate_password_hash

with app.app_context():
    if not User.query.filter_by(email='admin@example.com').first():
        admin = User(
            name='Admin',
            email='admin@example.com',
            phone='1234567890',
            password=generate_password_hash('admin123'),
            role='admin'
        )
        db.session.add(admin)
        db.session.commit()
        print("✅ Адмін створений!")
    else:
        print("ℹ️ Адмін уже існує.")
