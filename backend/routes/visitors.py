from flask import Blueprint, request, jsonify
from models import db, Visitor

visitors_bp = Blueprint('visitors', __name__)

@visitors_bp.route('/register', methods=['POST'])
def register():
    data = request.json
    if not data.get('name'):
        return jsonify({'error': 'Name is required'}), 400

    visitor = Visitor(
        name=data['name'],
        email=data.get('email', ''),
        phone=data.get('phone', ''),
        company=data.get('company', ''),
        photo=data.get('photo', '')
    )
    db.session.add(visitor)
    db.session.commit()
    return jsonify({'message': 'Visitor registered!', 'visitor': visitor.to_dict()}), 201

@visitors_bp.route('/', methods=['GET'])
def get_visitors():
    visitors = Visitor.query.order_by(Visitor.created_at.desc()).all()
    return jsonify([v.to_dict() for v in visitors]), 200

@visitors_bp.route('/<int:visitor_id>', methods=['GET'])
def get_visitor(visitor_id):
    visitor = Visitor.query.get_or_404(visitor_id)
    return jsonify(visitor.to_dict()), 200