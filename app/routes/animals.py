from flask import Blueprint, request, jsonify
from extensions import db
from models import Animal

animals_bp = Blueprint('animals', __name__, url_prefix='/api/animals')

@animals_bp.get('')
def list_animals():
    """List all monitored animals."""
    try:
        animals = Animal.query.all()
        return jsonify({
            'count': len(animals),
            'animals': [a.to_dict() for a in animals]
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@animals_bp.post('')
def create_animal():
    """Create a new animal record."""
    data = request.get_json()
    
    required_fields = ['animal_code', 'species']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
    
    try:
        animal = Animal(
            animal_code=data['animal_code'],
            species=data['species'],
            collar_id=data.get('collar_id'),
            status=data.get('status', 'ACTIVE')
        )
        
        db.session.add(animal)
        db.session.commit()
        
        return jsonify(animal.to_dict()), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@animals_bp.get('/<animal_id>')
def get_animal(animal_id):
    """Get animal details."""
    try:
        animal = Animal.query.get(animal_id)
        
        if not animal:
            return jsonify({'error': 'Animal not found'}), 404
        
        return jsonify(animal.to_dict()), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@animals_bp.put('/<animal_id>')
def update_animal(animal_id):
    """Update animal details."""
    data = request.get_json()
    
    try:
        animal = Animal.query.get(animal_id)
        
        if not animal:
            return jsonify({'error': 'Animal not found'}), 404
        
        animal.species = data.get('species', animal.species)
        animal.status = data.get('status', animal.status)
        
        db.session.commit()
        
        return jsonify(animal.to_dict()), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@animals_bp.get('/<animal_id>/trajectory')
def get_trajectory(animal_id):
    """Get animal trajectory."""
    from models import GPSEvent
    
    try:
        limit = request.args.get('limit', 50, type=int)
        
        events = GPSEvent.query.filter_by(animal_id=animal_id)\
            .order_by(GPSEvent.timestamp)\
            .limit(limit)\
            .all()
        
        return jsonify({
            'animal_id': animal_id,
            'trajectory': [e.to_dict() for e in events]
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
