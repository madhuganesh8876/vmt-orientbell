from flask import Blueprint, request, jsonify
from flask_mail import Message
from models import db, Visit, Visitor, User, Notification, Badge
from datetime import datetime, timedelta
import os

visits_bp = Blueprint('visits', __name__)

def send_email(to, subject, body):
    try:
        from app import mail
        msg = Message(subject, sender=os.getenv('MAIL_USERNAME'), recipients=[to])
        msg.body = body
        mail.send(msg)
    except Exception as e:
        print(f"Email error: {e}")

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
        status='pending',
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

@visits_bp.route('/approve/<int:visit_id>', methods=['PUT'])
def approve(visit_id):
    visit = Visit.query.get_or_404(visit_id)
    visit.status = 'active'
    db.session.flush()

    # Send approval email to visitor
    if visit.visitor and visit.visitor.email:
        send_email(
            to=visit.visitor.email,
            subject='✅ Your Visit is Approved — Orientbell VMT',
            body=f"""Dear {visit.visitor.name},

Your visit to Orientbell has been approved!

Visit Details:
- Host: {visit.host.name} ({visit.host.department})
- Purpose: {visit.purpose}
- Plant: {visit.plant}
- Check-in Time: {visit.check_in.strftime('%d %b %Y, %I:%M %p')}

Please proceed to meet your host. Show your badge code VMT-{visit.id} to security.

Regards,
Orientbell Visitor Management System
"""
        )

    db.session.commit()
    return jsonify({'message': 'Visit approved!', 'visit': visit.to_dict()}), 200

@visits_bp.route('/reject/<int:visit_id>', methods=['PUT'])
def reject(visit_id):
    visit = Visit.query.get_or_404(visit_id)
    data = request.json or {}
    message = data.get('message', 'Host is not available right now.')
    visit.status = 'rejected'
    db.session.flush()

    notification = Notification(
        host_id=visit.host_id,
        visit_id=visit.id,
        message=f"Busy notification sent: {message}"
    )
    db.session.add(notification)

    # Send email to visitor
    if visit.visitor and visit.visitor.email:
        send_email(
            to=visit.visitor.email,
            subject='ℹ️ Update on Your Visit — Orientbell VMT',
            body=f"""Dear {visit.visitor.name},

We wanted to update you regarding your visit to Orientbell.

Message from {visit.host.name}:
"{message}"

Visit Details:
- Host: {visit.host.name} ({visit.host.department})
- Purpose: {visit.purpose}
- Plant: {visit.plant}

Please check with the receptionist for further assistance.

Regards,
Orientbell Visitor Management System
"""
        )

    db.session.commit()
    return jsonify({'message': 'Marked as busy!', 'visit': visit.to_dict()}), 200

@visits_bp.route('/reschedule/<int:visit_id>', methods=['PUT'])
def reschedule(visit_id):
    visit = Visit.query.get_or_404(visit_id)
    data = request.json or {}
    message = data.get('message', 'Please come at another time.')
    scheduled_time = data.get('scheduled_time', '')
    visit.status = 'rescheduled'
    db.session.flush()

    notification = Notification(
        host_id=visit.host_id,
        visit_id=visit.id,
        message=f"Reschedule requested: {message}"
    )
    db.session.add(notification)

    # Format scheduled time nicely
    try:
        dt = datetime.strptime(scheduled_time, '%Y-%m-%dT%H:%M')
        formatted_time = dt.strftime('%d %b %Y at %I:%M %p')
    except:
        formatted_time = scheduled_time

    # Send email to visitor
    if visit.visitor and visit.visitor.email:
        send_email(
            to=visit.visitor.email,
            subject='📅 Visit Rescheduled — Orientbell VMT',
            body=f"""Dear {visit.visitor.name},

Your visit to Orientbell has been rescheduled.

Message from {visit.host.name}:
"{message}"

New Suggested Time: {formatted_time}

Visit Details:
- Host: {visit.host.name} ({visit.host.department})
- Purpose: {visit.purpose}
- Plant: {visit.plant}

Please come back at the suggested time. We look forward to meeting you!

Regards,
Orientbell Visitor Management System
"""
        )

    db.session.commit()
    return jsonify({'message': 'Rescheduled!', 'visit': visit.to_dict()}), 200

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

@visits_bp.route('/all', methods=['GET'])
def get_all():
    visits = Visit.query.order_by(Visit.check_in.desc()).limit(100).all()
    return jsonify([v.to_dict() for v in visits]), 200