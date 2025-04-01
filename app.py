import os
from dotenv import load_dotenv
from flask import Flask, render_template
from extensions import db, migrate
from routes.api_booking_multi import api_bp



load_dotenv()

app = Flask(__name__, static_folder='static', template_folder='templates')
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('SQLALCHEMY_DATABASE_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
migrate.init_app(app, db)

from routes.dashboard_routes import dashboard_bp
from routes.auth_routes import auth_bp
from routes.booking_routes import booking_bp
from routes.admin_routes import admin_bp
from routes.public_routes import public_bp
app.register_blueprint(public_bp)


app.register_blueprint(dashboard_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(booking_bp)
app.register_blueprint(admin_bp, url_prefix='/admin')

app.register_blueprint(api_bp)

@app.route('/')
def index():
    return render_template('index.html')


from routes.api_availability_extended import availability_bp
app.register_blueprint(availability_bp)


if __name__ == '__main__':
    app.run(debug=True)
