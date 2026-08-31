from extensions import db
from geoalchemy2 import Geography
from datetime import datetime

class GPSEvent(db.Model):
    """GPS event model for animal telemetry."""
    __tablename__ = 'gps_events'
    
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    animal_id = db.Column(db.String(36), db.ForeignKey('animals.id'), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    speed = db.Column(db.Float)
    heading = db.Column(db.Float)
    location = db.Column(Geography(geometry_type='POINT', srid=4326))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        db.Index('idx_gps_location', 'location', postgresql_using='gist'),
        db.Index('idx_gps_timestamp', 'timestamp'),
        db.Index('idx_gps_animal_id', 'animal_id'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'animal_id': self.animal_id,
            'timestamp': self.timestamp.isoformat(),
            'latitude': self.latitude,
            'longitude': self.longitude,
            'speed': self.speed,
            'heading': self.heading,
            'created_at': self.created_at.isoformat()
        }
    
    def __repr__(self):
        return f'<GPSEvent {self.animal_id} @ {self.timestamp}>'
