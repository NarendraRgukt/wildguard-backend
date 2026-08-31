from extensions import db
from datetime import datetime
import uuid

class Alert(db.Model):
    """Alert model for risk notifications."""
    __tablename__ = 'alerts'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    animal_id = db.Column(db.String(36), db.ForeignKey('animals.id'), nullable=False)
    threat_type = db.Column(db.String(100), nullable=False)  # railway, village, human-conflict
    severity = db.Column(db.String(20), nullable=False)  # LOW, MEDIUM, HIGH, CRITICAL
    risk_score = db.Column(db.Integer)  # 0-100
    description = db.Column(db.Text)
    evidence = db.Column(db.JSON)  # structured evidence
    investigation_summary = db.Column(db.Text)
    status = db.Column(db.String(50), default='DETECTED')  # DETECTED, EVALUATING, VERIFIED, FALSE_POSITIVE, RESOLVED
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    acknowledged_at = db.Column(db.DateTime)
    resolved_at = db.Column(db.DateTime)
    
    __table_args__ = (
        db.Index('idx_alert_animal_id', 'animal_id'),
        db.Index('idx_alert_status', 'status'),
        db.Index('idx_alert_created_at', 'created_at'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'animal_id': self.animal_id,
            'threat_type': self.threat_type,
            'severity': self.severity,
            'risk_score': self.risk_score,
            'description': self.description,
            'evidence': self.evidence,
            'investigation_summary': self.investigation_summary,
            'status': self.status,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'acknowledged_at': self.acknowledged_at.isoformat() if self.acknowledged_at else None,
            'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None
        }
    
    def __repr__(self):
        return f'<Alert {self.id} - {self.threat_type}>'
