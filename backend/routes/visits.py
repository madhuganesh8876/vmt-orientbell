from flask import Blueprint, request, jsonify
from models import db, Visit, Visitor, User, Notification, Badge
from datetime import datetime, timedelta

visits_bp = Blueprint('visits', __name__)

@visits_bp.route('/checkin', methods=['POST'])
def checkin():
    data = request.json

    visitor = None
    if data.get('visitor_id'):
        visitor = Visitor.query.get(data['visitor_id'])
    else:
        visitor = Visitor(
            name=data['visitor_name'],
            email=data.get('visitor_email', ''),
            phone=data.get('visitor_phone', ''),
            company=data.get('visitor_company', '')
        )
        db.session.add(visitor)
        db.session.flush()

    host = User.query.get(data['host_id'])
    if not host:
        return jsonify({'error': 'Host not found'}), 404

    visit = Visit(
        visitor_id=visitor.id,
        host_id=data['host_id'],
        purpose=data.get('purpose', ''),
        status='active',
        plant=data.get('plant', 'Plant 1')
    )
    db.session.add(visit)
    db.session.flush()

    badge = Badge(
        visit_id=visit.id,
        qr_data=f"VMT-{visit.id}-{visitor.name}-{datetime.utcnow().strftime('%Y%m%d')}",
        expiry=datetime.utcnow() + timedelta(hours=8)
    )
    db.session.add(badge)

    notification = Notification(
        host_id=host.id,
        visit_id=visit.id,
        message=f"{visitor.name} from {visitor.company} has arrived to meet you."
    )
    db.session.add(notification)
    db.session.commit()

    return jsonify({
        'message': 'Checked in successfully!',
        'visit': visit.to_dict(),
        'badge': badge.to_dict()
    }), 201

@visits_bp.route('/checkout/<int:visit_id>', methods=['PUT'])
def checkout(visit_id):
    visit = Visit.query.get_or_404(visit_id)
    visit.check_out = datetime.utcnow()
    visit.status = 'checked_out'
    db.session.commit()
    return jsonify({'message': 'Checked out!', 'visit': visit.to_dict()}), 200

@visits_bp.route('/active', methods=['GET'])
def get_active():
    visits = Visit.query.filter_by(status='active').order_by(Visit.check_in.desc()).all()
    return jsonify([v.to_dict() for v in visits]), 200

@visits_bp.route('/today', methods=['GET'])
def get_today():
    today = datetime.utcnow().date()
    visits = Visit.query.filter(
        db.func.date(Visit.check_in) == today
    ).order_by(Visit.check_in.desc()).all()
    return jsonify([v.to_dict() for v in visits]), 200

@visits_bp.route('/approve/<int:visit_id>', methods=['PUT'])
def approve(visit_id):
    visit = Visit.query.get_or_404(visit_id)
    visit.status = 'active'
    db.session.commit()
    return jsonify({'message': 'Visit approved!', 'visit': visit.to_dict()}), 200

@visits_bp.route('/all', methods=['GET'])
def get_all():
    visits = Visit.query.order_by(Visit.check_in.desc()).limit(100).all()
    return jsonify([v.to_dict() for v in visits]), 200