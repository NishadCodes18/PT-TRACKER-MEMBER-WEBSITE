import secrets
from datetime import datetime

from flask import Blueprint, current_app, flash, redirect, render_template, request, session, url_for
from flask_login import current_user, login_required, login_user, logout_user
from werkzeug.security import check_password_hash

from backend.database import db
from backend.extensions import limiter
from backend.models import Client, Trainer, EmailLog
from member_app.models_member import MemberOTP
from backend.utils.mail import send_html_email

member_auth_bp = Blueprint('member_auth', __name__, url_prefix='/auth')


def _send_member_otp(client, otp):
    gym_name = current_app.config.get('GYM_NAME', 'Gym Tracker')
    subject = f"{gym_name} - Login Code"
    expiry_minutes = current_app.config.get('PASSWORD_RESET_OTP_MINUTES', 10)

    sent = send_html_email(
        client.email,
        subject,
        'member_login_otp',
        member_name=client.name,
        otp_code=otp,
        expiry_minutes=expiry_minutes,
        gym_name=gym_name,
    )

    if client.trainer_id:
        log_entry = EmailLog(
            trainer_id=client.trainer_id,
            recipient_email=client.email,
            recipient_name=client.name,
            subject=subject,
            email_type='member_login_otp',
            status='sent' if sent else 'failed',
            client_id=client.id,
            error_message=None if sent else 'SMTP delivery failed or SMTP credentials missing',
        )
        db.session.add(log_entry)
        db.session.commit()

    return sent


@member_auth_bp.route('/login', methods=['GET', 'POST'])
@limiter.limit('12 per minute')
def login():
    if current_user.is_authenticated:
        return redirect(url_for('member_portal.dashboard'))

    if request.method == 'GET':
        # Provide trainer dropdown list for GET requests
        trainers = Trainer.query.with_entities(Trainer.username).order_by(Trainer.username).all()
        trainer_names = [t[0] for t in trainers]
        return render_template('member_login.html', trainers=trainer_names)
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        trainer_name = request.form.get('trainer_name', '').strip()

        if not email or not trainer_name:
            flash('Email and trainer name are required', 'error')
            # Repopulate trainer list on error
            trainers = Trainer.query.with_entities(Trainer.username).order_by(Trainer.username).all()
            trainer_names = [t[0] for t in trainers]
            return render_template('member_login.html', trainers=trainer_names)

        # Find trainer by name
        trainer = Trainer.query.filter(Trainer.username.ilike(trainer_name)).first()
        if not trainer:
            flash('Trainer not found. Please check the trainer name.', 'error')
            trainers = Trainer.query.with_entities(Trainer.username).order_by(Trainer.username).all()
            trainer_names = [t[0] for t in trainers]
            return render_template('member_login.html', trainers=trainer_names)

        # Find client by email and trainer
        client = Client.query.filter_by(email=email, trainer_id=trainer.id).first()
        if not client:
            flash('Member not found. Please check your email and trainer name.', 'error')
            trainers = Trainer.query.with_entities(Trainer.username).order_by(Trainer.username).all()
            trainer_names = [t[0] for t in trainers]
            return render_template('member_login.html', trainers=trainer_names)

        # Generate OTP
        otp = f"{secrets.randbelow(1000000):06d}"
        record = MemberOTP.query.filter_by(client_id=client.id).first()
        if not record:
            record = MemberOTP(client_id=client.id, otp_hash='pending', expires_at=datetime.utcnow())
        record.store_otp(otp, current_app.config.get('PASSWORD_RESET_OTP_MINUTES', 10))
        db.session.add(record)
        db.session.commit()

        if _send_member_otp(client, otp):
            session['member_login_client_id'] = client.id
            flash('OTP sent to your email. Enter it to continue.', 'success')
            return redirect(url_for('member_auth.verify_otp'))

        flash('Unable to send OTP. Please contact your trainer.', 'error')
        trainers = Trainer.query.with_entities(Trainer.username).order_by(Trainer.username).all()
        trainer_names = [t[0] for t in trainers]
        return render_template('member_login.html', trainers=trainer_names)

    # For any other method (should not happen) fall back to GET behavior
    trainers = Trainer.query.with_entities(Trainer.username).order_by(Trainer.username).all()
    trainer_names = [t[0] for t in trainers]
    return render_template('member_login.html', trainers=trainer_names)


@member_auth_bp.route('/verify-otp', methods=['GET', 'POST'])
@limiter.limit('20 per hour')
def verify_otp():
    if current_user.is_authenticated:
        return redirect(url_for('member_portal.dashboard'))

    client_id = session.get('member_login_client_id')
    if not client_id:
        flash('Please start the login process again.', 'info')
        return redirect(url_for('member_auth.login'))

    client = Client.query.get(client_id)
    record = MemberOTP.query.filter_by(client_id=client_id).first()
    if not client or not record:
        flash('Start the login process again.', 'info')
        return redirect(url_for('member_auth.login'))

    if request.method == 'POST':
        otp = request.form.get('otp', '').strip()
        max_attempts = current_app.config.get('PASSWORD_RESET_MAX_ATTEMPTS', 5)

        if not otp or len(otp) != 6 or not otp.isdigit():
            flash('Enter the 6-digit code from your email.', 'error')
            return render_template('member_verify_otp.html', client=client)

        if record.is_expired():
            flash('That OTP has expired. Request a new one.', 'error')
            return redirect(url_for('member_auth.login'))

        if not record.can_retry(max_attempts):
            flash('Too many invalid attempts. Request a new OTP.', 'error')
            return redirect(url_for('member_auth.login'))

        if not check_password_hash(record.otp_hash, otp):
            record.attempts += 1
            db.session.commit()
            flash('Invalid OTP. Please try again.', 'error')
            return render_template('member_verify_otp.html', client=client)

        # OTP verified, log in the client
        session.pop('member_login_client_id', None)
        login_user(client, remember=True)
        flash('Login successful!', 'success')
        return redirect(url_for('member_portal.dashboard'))

    return render_template('member_verify_otp.html', client=client)


@member_auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    session.pop('member_login_client_id', None)
    flash('You have been logged out', 'info')
    return redirect(url_for('member_auth.login'))
