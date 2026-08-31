from flask import Blueprint, request, jsonify
from extensions import db
from models import Animal, GPSEvent, Geofence
from gps.simulator import GPSSimulator
from geo.geofence import GeofenceService
from datetime import datetime

gps_bp = Blueprint('gps', __name__, url_prefix='/api/gps')

@gps_bp.post('')
def ingest_gps():
    """Ingest GPS data from simulator or device."""
    data = request.get_json()
    
    # Validate input
    required_fields = ['animal_id', 'latitude', 'longitude', 'speed', 'heading', 'timestamp']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
    
    try:
        # Parse timestamp
        if isinstance(data['timestamp'], str):
            timestamp = datetime.fromisoformat(data['timestamp'].replace('Z', '+00:00'))
        else:
            timestamp = datetime.utcnow()
        
        # Create GPS event
        from geoalchemy2.elements import WKTElement
        gps_event = GPSEvent(
            animal_id=data['animal_id'],
            timestamp=timestamp,
            latitude=data['latitude'],
            longitude=data['longitude'],
            speed=data['speed'],
            heading=data['heading'],
            location=WKTElement(f"POINT({data['longitude']} {data['latitude']})", srid=4326)
        )
        
        db.session.add(gps_event)
        db.session.commit()
        
        return jsonify({
            'status': 'accepted',
            'event_id': gps_event.id,
            'animal_id': data['animal_id']
        }), 202
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@gps_bp.get('/animal/<animal_id>/latest')
def get_latest_gps(animal_id):
    """Get latest GPS position for an animal."""
    try:
        lat_gps = GPSEvent.query.filter_by(animal_id=animal_id).order_by(GPSEvent.timestamp.desc()).first()
        
        if not lat_gps:
            return jsonify({'error': 'No GPS data found'}), 404
        
        return jsonify(lat_gps.to_dict()), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@gps_bp.get('/animal/<animal_id>/history')
def get_gps_history(animal_id):
    """Get GPS history for an animal."""
    try:
        limit = request.args.get('limit', 100, type=int)
        
        gps_events = GPSEvent.query.filter_by(animal_id=animal_id)\
            .order_by(GPSEvent.timestamp.desc())\
            .limit(limit)\
            .all()
        
        return jsonify({
            'animal_id': animal_id,
            'events': [e.to_dict() for e in reversed(gps_events)]
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
