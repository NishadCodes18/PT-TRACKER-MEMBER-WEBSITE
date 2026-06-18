"""Vercel serverless function entry point for member portal."""
import os
import sys
import logging

# Set up logging
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

# Add parent directories to path so we can import from backend
current_dir = os.path.dirname(__file__)
member_website_dir = os.path.abspath(os.path.join(current_dir, '..'))
parent_dir = os.path.abspath(os.path.join(member_website_dir, '..'))
sys.path.insert(0, parent_dir)
sys.path.insert(0, member_website_dir)

# Set Vercel flag if not already set
os.environ.setdefault('VERCEL', 'true')

# Load environment variables only if .env exists
try:
    from dotenv import load_dotenv
    env_path = os.path.join(parent_dir, '.env')
    if os.path.exists(env_path):
        load_dotenv(env_path)
except Exception:
    pass

# Initialize app
app = None
try:
    from member_app import create_member_app
    app = create_member_app()
    logger.info("Member portal app created successfully")
except Exception as e:
    error_message = str(e)
    logger.error(f"Failed to create member portal app: {error_message}", exc_info=True)
    from flask import Flask, jsonify
    app = Flask(__name__)

    @app.route('/')
    @app.route('/<path:path>')
    def error_handler(path=''):
        return jsonify({
            "error": "Member portal failed to initialize",
            "message": error_message,
            "hint": "Check DATABASE_URL is set correctly and backend modules are accessible"
        }), 500

# Export app for Vercel
handler = app
