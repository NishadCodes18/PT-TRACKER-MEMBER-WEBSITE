from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from backend.database import db


class MemberOTP(db.Model):
    """Store one-time passwords for member email-based authentication."""
    __tablename__ = 'member_otps'

    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id', ondelete='CASCADE'), nullable=False, unique=True)
    otp_hash = db.Column(db.String(256), nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    attempts = db.Column(db.Integer, nullable=False, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def store_otp(self, otp, expires_minutes=10):
        self.otp_hash = generate_password_hash(str(otp), method='pbkdf2:sha256')
        self.expires_at = datetime.utcnow() + timedelta(minutes=expires_minutes)
        self.attempts = 0

    def is_expired(self):
        return datetime.utcnow() > self.expires_at

    def can_retry(self, max_attempts=5):
        return self.attempts < max_attempts
