import logging
import os
import sys

from flask import Flask, redirect, render_template, request, url_for
from flask_login import LoginManager
from sqlalchemy import text

# Add parent directory to path to import shared database
parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, parent_dir)

from backend.database import db
from backend.config import Config
from backend.extensions import csrf, limiter


def create_member_app(config_class=Config):
    """Application factory for member portal"""
    app = Flask(
        __name__,
        template_folder=os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates"),
        static_folder=os.path.join(os.path.dirname(os.path.dirname(__file__)), "static"),
    )
    app.config.from_object(config_class)
    app.config['DB_INITIALIZED'] = False

    if app.config.get("SECRET_KEY") == "dev-secret-key-change-in-prod" and app.config.get("IS_PRODUCTION"):
        raise RuntimeError("Set a strong SECRET_KEY environment variable before running in production.")

    log_level = str(app.config.get("LOG_LEVEL", "WARNING")).upper()
    app.logger.setLevel(getattr(logging, log_level, logging.WARNING))

    db.init_app(app)
    csrf.init_app(app)
    limiter.init_app(app)

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = "member_auth.login"
    login_manager.login_message = "Please log in to access your membership details."
    login_manager.session_protection = "strong"

    @login_manager.user_loader
    def load_user(user_id):
        from backend.models import Client
        try:
            return Client.query.get(int(user_id))
        except (TypeError, ValueError):
            return None

    @app.context_processor
    def inject_csrf():
        from flask_wtf.csrf import generate_csrf
        return dict(csrf_token=generate_csrf)

    @app.before_request
    def check_db_initialization():
        if (request.path.startswith('/static/') or
            request.path == '/health' or
            request.path == '/favicon.ico' or
            request.path == '/favicon.png'):
            return None

        if not app.config.get('DB_INITIALIZED', False):
            try:
                app.logger.info("[RETRY] Attempting database initialization...")
                connection = db.engine.connect()
                connection.close()
                db.create_all()
                app.config['DB_INITIALIZED'] = True
                app.logger.info("[OK] Database initialized successfully")
                return None
            except Exception as e:
                app.logger.error(f"[ERROR] Database initialization failed: {e}")
                return render_template('loading.html'), 503

    @app.after_request
    def _add_security_headers(response):
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault("X-Content-Type-Options", "nosniff")

        if request.path.startswith('/static/'):
            response.headers['Cache-Control'] = 'public, max-age=31536000, immutable'
        elif request.endpoint and str(request.endpoint).startswith("member_auth."):
            response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
        else:
            response.headers['Cache-Control'] = 'public, max-age=60'

        return response

    with app.app_context():
        try:
            app.logger.info("[OK] Testing database connection...")
            connection = db.engine.connect()
            connection.close()
            app.logger.info("[OK] Database connection successful")
            db.create_all()
            app.config['DB_INITIALIZED'] = True
        except Exception as e:
            app.logger.error(f"[ERROR] DATABASE ERROR: {e}", exc_info=True)
            if not os.environ.get('VERCEL') == 'true':
                raise

    from .routes.member_auth import member_auth_bp
    from .routes.member_portal import member_portal_bp

    app.register_blueprint(member_auth_bp)
    app.register_blueprint(member_portal_bp)

    @app.route("/")
    def index():
        if not app.config.get('DB_INITIALIZED', False):
            return render_template('loading.html')
        return render_template('portal_landing.html')

    @app.route("/health")
    def health():
        db_ready = app.config.get('DB_INITIALIZED', False)
        return {
            "ok": db_ready,
            "status": "healthy" if db_ready else "initializing",
            "db_initialized": db_ready
        }

    return app
