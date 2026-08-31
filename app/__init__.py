from flask import Flask, jsonify
from extensions import db, migrate, cors, init_extensions
from config import config
import os

def create_app(config_name=None):
    """Application factory function."""
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')
    
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    init_extensions(app)
    
    # Register blueprints
    from routes.gps import gps_bp
    from routes.animals import animals_bp
    from routes.alerts import alerts_bp
    from routes.cameras import cameras_bp
    
    app.register_blueprint(gps_bp)
    app.register_blueprint(animals_bp)
    app.register_blueprint(alerts_bp)
    app.register_blueprint(cameras_bp)
    
    # Health check endpoint
    @app.route('/health', methods=['GET'])
    def health():
        return jsonify({'status': 'healthy'}), 200
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return jsonify({'error': 'Internal server error'}), 500
    
    # Create tables
    with app.app_context():
        db.create_all()
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
