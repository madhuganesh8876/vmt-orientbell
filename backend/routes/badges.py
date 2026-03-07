from flask import Blueprint, send_file, jsonify
from models import db, Badge
import qrcode
import io

badges_bp = Blueprint('badges', __name__)

@badges_bp.route('/<int:visit_id>', methods=['GET'])
def get_badge(visit_id):
    badge = Badge.query.filter_by(visit_id=visit_id).first()
    if not badge:
        return jsonify({'error': 'Badge not found'}), 404
    return jsonify(badge.to_dict()), 200

@badges_bp.route('/qr/<int:visit_id>', methods=['GET'])
def generate_qr(visit_id):
    badge = Badge.query.filter_by(visit_id=visit_id).first()
    if not badge:
        return jsonify({'error': 'Badge not found'}), 404

    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(badge.qr_data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="#1A3C6E", back_color="white")

    img_io = io.BytesIO()
    img.save(img_io, 'PNG')
    img_io.seek(0)
    return send_file(img_io, mimetype='image/png')