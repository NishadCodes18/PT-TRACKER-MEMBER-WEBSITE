from datetime import datetime
from flask import Blueprint, render_template
from flask_login import current_user, login_required

from backend.models import Client, Trainer

member_portal_bp = Blueprint('member_portal', __name__)


@member_portal_bp.route('/dashboard')
@login_required
def dashboard():
    client = current_user
    trainer = Trainer.query.get(client.trainer_id) if client.trainer_id else None

    return render_template('member_dashboard.html', client=client, trainer=trainer, now=datetime.now().date())
