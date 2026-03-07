from flask import Blueprint, request, jsonify
from models import db, Visit
from datetime import datetime, timedelta
from sqlalchemy import func

reports_bp = Blueprint('reports', __name__)

@reports_bp.route('/summary', methods=['GET'])
def summary():
    today = datetime.utcnow().date()
    month_start = today.replace(day=1)

    total_today = Visit.query.filter(func.date(Visit.check_in) == today).count()
    active_now = Visit.query.filter_by(status='active').count()
    total_month = Visit.query.filter(func.date(Visit.check_in) >= month_start).count()
    total_all = Visit.query.count()

    traffic = []
    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        count = Visit.query.filter(func.date(Visit.check_in) == day).count()
        traffic.append({'date': day.strftime('%d %b'), 'count': count})

    purposes = db.session.query(
        Visit.purpose, func.count(Visit.id)
    ).group_by(Visit.purpose).all()
    purpose_data = [{'purpose': p[0] or 'Other', 'count': p[1]} for p in purposes]

    plants = db.session.query(
        Visit.plant, func.count(Visit.id)
    ).group_by(Visit.plant).all()
    plant_data = [{'plant': p[0] or 'Unknown', 'count': p[1]} for p in plants]

    return jsonify({
        'total_today': total_today,
        'active_now': active_now,
        'total_month': total_month,
        'total_all': total_all,
        'traffic_7days': traffic,
        'purpose_breakdown': purpose_data,
        'plant_breakdown': plant_data
    }), 200

@reports_bp.route('/visitor-flow', methods=['GET'])
def visitor_flow():
    start = request.args.get('start')
    end = request.args.get('end')
    plant = request.args.get('plant', '')

    query = Visit.query
    if start:
        query = query.filter(Visit.check_in >= start)
    if end:
        query = query.filter(Visit.check_in <= end)
    if plant:
        query = query.filter_by(plant=plant)

    visits = query.order_by(Visit.check_in.desc()).all()
    return jsonify([v.to_dict() for v in visits]), 200