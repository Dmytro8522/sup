from flask import Blueprint, request, redirect, url_for, render_template, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        phone = request.form.get('phone')
        email = request.form.get('email')
        password = request.form.get('password')
        role = request.form.get('role', 'user')  # По умолчанию все пользователи - обычные пользователи
        if not (name and phone and email and password):
            return "Будь ласка, заповніть усі поля", 400
        if User.query.filter_by(email=email).first():
            return "Користувач з таким email вже існує", 400
        new_user = User(name=name, phone=phone, email=email,
                        password=generate_password_hash(password), role=role)
        db.session.add(new_user)
        db.session.commit()
        session['user_id'] = new_user.id
        session['role'] = new_user.role
        if new_user.role == 'admin':
            return redirect(url_for('admin.index'))  # Перенаправляем администратора в админ-панель
        return redirect(url_for('index'))
    return render_template('register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['role'] = user.role
            if user.role == 'admin':
                return redirect(url_for('admin.index'))  # Перенаправляем администратора
            return redirect(url_for('index'))
        return "Невірний email або пароль", 401
    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))
