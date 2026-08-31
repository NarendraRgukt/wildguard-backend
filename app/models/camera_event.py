from extensions import db
from datetime import datetime
import uuid

class CameraEvent(db.Model):
    """Camera event model for CCTV detections."""
    __tablename__ = 'camera_events'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    animal_id = db.Column(db.String(36), db.ForeignKey('animals.id'), nullable=True)
    camera_id = db.Column(db.String(100), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False)
    object_type = db.Column(db.String(50), nullable=False)  # animal, human, vehicle
    species = db.Column(db.String(100))
    confidence = db.Column(db.Float)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    image_path = db.Column(db.String(500))
    bbox = db.Column(db.JSON)  # [x1, y1, x2, y2]
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        db.Index('idx_camera_event_timestamp', 'timestamp'),
        db.Index('idx_camera_event_animal_id', 'animal_id'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'animal_id': self.animal_id,
            'camera_id': self.camera_id,
            'timestamp': self.timestamp.isoformat(),
            'object_type': self.object_type,
            'species': self.species,
            'confidence': self.confidence,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'image_path': self.image_path,
            'bbox': self.bbox,
            'created_at': self.created_at.isoformat()
        }
    
    def __repr__(self):
        return f'<CameraEvent {self.camera_id} @ {self.timestamp}>'
