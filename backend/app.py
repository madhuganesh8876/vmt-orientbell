from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_mail import Mail
from dotenv import load_dotenv
from models import db
import os

load_dotenv()

app = Flask(__name__)
CORS(app, origins="*")

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'mysql+mysqlconnector://root:yourpassword@localhost/vmt_db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_size': 1,
    'max_overflow': 0,
    'pool_recycle': 180,
    'pool_pre_ping': True,
    'pool_timeout': 30
}
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET', 'vmt-secret-key-orientbell-2025')
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')

db.init_app(app)
jwt = JWTManager(app)
mail = Mail(app)

from routes.auth import auth_bp
from routes.visitors import visitors_bp
from routes.visits import visits_bp
from routes.badges import badges_bp
from routes.reports import reports_bp
from routes.notifications import notifications_bp

app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(visitors_bp, url_prefix='/api/visitors')
app.register_blueprint(visits_bp, url_prefix='/api/visits')
app.register_blueprint(badges_bp, url_prefix='/api/badges')
app.register_blueprint(reports_bp, url_prefix='/api/reports')
app.register_blueprint(notifications_bp, url_prefix='/api/notifications')

@app.route('/')
def home():
    return {'message': 'VMT API is running!', 'status': 'ok'}

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        print("Database tables created!")
    app.run(debug=True, port=5000)