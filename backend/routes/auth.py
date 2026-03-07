from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Email and password required'}), 400

    user = User.query.filter_by(email=data['email']).first()
    if not user or not check_password_hash(user.password, data['password']):
        return jsonify({'error': 'Invalid email or password'}), 401

    token = create_access_token(identity=str(user.id))
    return jsonify({'token': token, 'user': user.to_dict()}), 200

@auth_bp.route('/register-user', methods=['POST'])
def register_user():
    data = request.json
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already exists'}), 400

    hashed_pw = generate_password_hash(data['password'])
    user = User(
        name=data['name'],
        email=data['email'],
        password=hashed_pw,
        role=data['role'],
        department=data.get('department', ''),
        plant=data.get('plant', '')
    )
    db.session.add(user)
    db.session.commit()
    return jsonify({'message': 'User created!', 'user': user.to_dict()}), 201

@auth_bp.route('/me', methods=['GET'])
def me():
    return jsonify({'message': 'ok'}), 200

@auth_bp.route('/hosts', methods=['GET'])
def get_hosts():
    hosts = User.query.filter_by(role='host').all()
    return jsonify([h.to_dict() for h in hosts]), 200