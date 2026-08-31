from flask import Blueprint, request, jsonify
from extensions import db
from models import Alert, Animal

alerts_bp = Blueprint('alerts', __name__, url_prefix='/api/alerts')

@alerts_bp.get('')
def list_alerts():
    """List all alerts."""
    try:
        status = request.args.get('status', None)
        limit = request.args.get('limit', 100, type=int)
        
        query = Alert.query.order_by(Alert.created_at.desc())
        
        if status:
            query = query.filter_by(status=status)
        
        alerts = query.limit(limit).all()
        
        return jsonify({
            'count': len(alerts),
            'alerts': [a.to_dict() for a in alerts]
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@alerts_bp.post('')
def create_alert():
    """Create a new alert (usually called by risk engine)."""
    data = request.get_json()
    
    required_fields = ['animal_id', 'threat_type', 'severity', 'risk_score']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
    
    try:
        alert = Alert(
            animal_id=data['animal_id'],
            threat_type=data['threat_type'],
            severity=data['severity'],
            risk_score=data['risk_score'],
            description=data.get('description'),
            evidence=data.get('evidence'),
            investigation_summary=data.get('investigation_summary')
        )
        
        db.session.add(alert)
        db.session.commit()
        
        return jsonify(alert.to_dict()), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@alerts_bp.get('/<alert_id>')
def get_alert(alert_id):
    """Get alert details."""
    try:
        alert = Alert.query.get(alert_id)
        
        if not alert:
            return jsonify({'error': 'Alert not found'}), 404
        
        return jsonify(alert.to_dict()), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@alerts_bp.post('/<alert_id>/acknowledge')
def acknowledge_alert(alert_id):
    """Acknowledge an alert."""
    from datetime import datetime
    
    try:
        alert = Alert.query.get(alert_id)
        
        if not alert:
            return jsonify({'error': 'Alert not found'}), 404
        
        alert.status = 'EVALUATING'
        alert.acknowledged_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify(alert.to_dict()), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@alerts_bp.post('/<alert_id>/resolve')
def resolve_alert(alert_id):
    """Resolve an alert."""
    from datetime import datetime
    
    data = request.get_json()
    resolution = data.get('resolution', 'VERIFIED')
    
    try:
        alert = Alert.query.get(alert_id)
        
        if not alert:
            return jsonify({'error': 'Alert not found'}), 404
        
        alert.status = resolution  # VERIFIED or FALSE_POSITIVE
        alert.resolved_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify(alert.to_dict()), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
