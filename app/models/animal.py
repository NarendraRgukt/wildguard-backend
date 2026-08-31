from extensions import db
from datetime import datetime
import uuid

class Animal(db.Model):
    """Animal model for tracking monitored wildlife."""
    __tablename__ = 'animals'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    animal_code = db.Column(db.String(50), unique=True, nullable=False)
    species = db.Column(db.String(100))
    collar_id = db.Column(db.String(100))
    status = db.Column(db.String(50), default='ACTIVE')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    gps_events = db.relationship('GPSEvent', backref='animal', lazy=True, cascade='all, delete-orphan')
    camera_events = db.relationship('CameraEvent', backref='animal', lazy=True, cascade='all, delete-orphan')
    alerts = db.relationship('Alert', backref='animal', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'animal_code': self.animal_code,
            'species': self.species,
            'collar_id': self.collar_id,
            'status': self.status,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    def __repr__(self):
        return f'<Animal {self.animal_code}>'
