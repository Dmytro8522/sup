from flask import Blueprint, request, session, redirect, url_for, render_template, flash
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
        if not (name and phone and email and password):
            flash("Будь ласка, заповніть усі поля", "danger")
            return render_template('register.html')
        if User.query.filter_by(email=email).first():
            flash("Користувач з таким email вже існує", "danger")
            return render_template('register.html')
        new_user = User(name=name, phone=phone, email=email,
                        password=generate_password_hash(password), role='user')
        db.session.add(new_user)
        db.session.commit()
        flash("Реєстрація пройшла успішно, тепер увійдіть", "success")
        return redirect(url_for('auth.login'))
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
            session['name'] = user.name
            flash("Ви успішно увійшли!", "success")
            # Если пользователь администратор, перенаправляем в адмін-панель
            if user.role == 'admin':
                return redirect(url_for('admin.admin_index'))
            else:
                return redirect(url_for('dashboard.dashboard'))
        else:
            flash("Невірний email або пароль", "danger")
            return render_template('login.html')
    return render_template('login.html')


@auth_bp.route('/logout')
def logout():
    session.clear()
    flash("Ви вийшли", "info")
    return redirect(url_for('index'))
