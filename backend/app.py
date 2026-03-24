from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from config import Config
from models.db import db
from routes.auth import auth_bp
from routes.upload import upload_bp
from routes.report import report_bp
import os


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions
    CORS(app, origins=['http://localhost:5173', 'http://localhost:5174', 'http://localhost:3000'], supports_credentials=True)
    jwt = JWTManager(app)
    db.init_app(app)

    # Return 401 for all JWT errors instead of 422
    @jwt.invalid_token_loader
    def invalid_token_callback(error_string):
        return jsonify({'error': 'Invalid token', 'message': error_string}), 401

    @jwt.unauthorized_loader
    def missing_token_callback(error_string):
        return jsonify({'error': 'Missing token', 'message': error_string}), 401

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({'error': 'Token has expired'}), 401

    # Ensure upload directory exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(upload_bp, url_prefix='/api/upload')
    app.register_blueprint(report_bp, url_prefix='/api/reports')

    # Create database tables
    with app.app_context():
        db.create_all()

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000, exclude_patterns=['*.pyc', '*/site-packages/*'])
