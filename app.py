import os
from dotenv import load_dotenv
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, login_user, logout_user, login_required, current_user

# Загрузка переменных окружения из файла .env
load_dotenv()

app = Flask(__name__, static_folder='static', template_folder='templates')

# Конфигурация приложения
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('SQLALCHEMY_DATABASE_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Инициализация базы данных и миграций
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Инициализация Flask-Login
login_manager = LoginManager(app)
login_manager.login_view = 'auth.login'  # Указываем маршрут для перенаправления неаутентифицированных пользователей

@login_manager.user_loader
def load_user(user_id):
    from models import User  # Импортируем здесь, чтобы избежать циклических импортов
    return User.query.get(int(user_id))

# Регистрация маршрутов
from routes.auth_routes import auth_bp
from routes.booking_routes import booking_bp
from routes.admin_routes import admin_bp

app.register_blueprint(auth_bp)
app.register_blueprint(booking_bp)
app.register_blueprint(admin_bp)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/admin_page')
@login_required
def admin_page():
    return render_template('admin.html')
