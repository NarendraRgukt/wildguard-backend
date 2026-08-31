from extensions import db
from geoalchemy2 import Geography
from datetime import datetime

class Geofence(db.Model):
    """Geofence model for railway and village boundaries."""
    __tablename__ = 'geofences'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    type = db.Column(db.String(50), nullable=False)  # RAILWAY, VILLAGE, FOREST
    geometry = db.Column(Geography(geometry_type='GEOMETRY', srid=4326), nullable=False)
    risk_level = db.Column(db.String(20))  # LOW, MEDIUM, HIGH, CRITICAL
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (
        db.Index('idx_geofence_geometry', 'geometry', postgresql_using='gist'),
        db.Index('idx_geofence_type', 'type'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'type': self.type,
            'risk_level': self.risk_level,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    def __repr__(self):
        return f'<Geofence {self.name} ({self.type})>'
