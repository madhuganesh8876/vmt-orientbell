from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from datetime import datetime

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.Enum('admin', 'receptionist', 'host'), nullable=False)
    department = db.Column(db.String(100))
    plant = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'role': self.role,
            'department': self.department,
            'plant': self.plant
        }

class Visitor(db.Model):
    __tablename__ = 'visitors'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    company = db.Column(db.String(100))
    photo = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'company': self.company,
            'photo': self.photo,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M')
        }

class Visit(db.Model):
    __tablename__ = 'visits'
    id = db.Column(db.Integer, primary_key=True)
    visitor_id = db.Column(db.Integer, db.ForeignKey('visitors.id'))
    host_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    purpose = db.Column(db.String(200))
    check_in = db.Column(db.DateTime, default=datetime.utcnow)
    check_out = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.Enum('active', 'checked_out', 'pending'), default='pending')
    plant = db.Column(db.String(100))

    visitor = db.relationship('Visitor', backref='visits')
    host = db.relationship('User', backref='hosted_visits')

    def to_dict(self):
        return {
            'id': self.id,
            'visitor': self.visitor.to_dict() if self.visitor else None,
            'host': self.host.to_dict() if self.host else None,
            'purpose': self.purpose,
            'check_in': self.check_in.strftime('%Y-%m-%d %H:%M') if self.check_in else None,
            'check_out': self.check_out.strftime('%Y-%m-%d %H:%M') if self.check_out else None,
            'status': self.status,
            'plant': self.plant
        }

class Badge(db.Model):
    __tablename__ = 'badges'
    id = db.Column(db.Integer, primary_key=True)
    visit_id = db.Column(db.Integer, db.ForeignKey('visits.id'))
    qr_data = db.Column(db.Text)
    expiry = db.Column(db.DateTime)
    visit = db.relationship('Visit', backref='badge')

    def to_dict(self):
        return {
            'id': self.id,
            'visit_id': self.visit_id,
            'qr_data': self.qr_data,
            'expiry': self.expiry.strftime('%Y-%m-%d %H:%M') if self.expiry else None
        }

class Notification(db.Model):
    __tablename__ = 'notifications'
    id = db.Column(db.Integer, primary_key=True)
    host_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    visit_id = db.Column(db.Integer, db.ForeignKey('visits.id'))
    message = db.Column(db.String(255))
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    host = db.relationship('User', backref='notifications')
    visit = db.relationship('Visit', backref='notifications')

    def to_dict(self):
        return {
            'id': self.id,
            'host_id': self.host_id,
            'visit_id': self.visit_id,
            'message': self.message,
            'is_read': self.is_read,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M')
        }