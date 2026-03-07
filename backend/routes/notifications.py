from flask import Blueprint, jsonify
from models import db, Notification

notifications_bp = Blueprint('notifications', __name__)

@notifications_bp.route('/<int:host_id>', methods=['GET'])
def get_notifications(host_id):
    notifs = Notification.query.filter_by(host_id=host_id)\
        .order_by(Notification.created_at.desc()).all()
    return jsonify([n.to_dict() for n in notifs]), 200

@notifications_bp.route('/read/<int:notif_id>', methods=['PUT'])
def mark_read(notif_id):
    notif = Notification.query.get_or_404(notif_id)
    notif.is_read = True
    db.session.commit()
    return jsonify({'message': 'Marked as read'}), 200

@notifications_bp.route('/unread-count/<int:host_id>', methods=['GET'])
def unread_count(host_id):
    count = Notification.query.filter_by(host_id=host_id, is_read=False).count()
    return jsonify({'count': count}), 200