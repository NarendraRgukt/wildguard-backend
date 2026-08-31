class AlertManager:
    """Manages alert lifecycle and notifications."""
    
    SEVERITY_TO_ACTION = {
        'CRITICAL': ['email', 'sms', 'dashboard', 'alarm'],
        'HIGH': ['email', 'dashboard'],
        'MEDIUM': ['dashboard', 'log'],
        'LOW': ['log']
    }
    
    @staticmethod
    def create_alert(db, animal_id, threat_type, severity, risk_score, description, evidence, investigation_summary):
        """Create a new alert."""
        from models import Alert
        from datetime import datetime
        
        alert = Alert(
            animal_id=animal_id,
            threat_type=threat_type,
            severity=severity,
            risk_score=risk_score,
            description=description,
            evidence=evidence,
            investigation_summary=investigation_summary,
            status='DETECTED'
        )
        
        db.session.add(alert)
        db.session.commit()
        
        return alert
    
    @staticmethod
    def get_alert(db, alert_id):
        """Retrieve alert by ID."""
        from models import Alert
        return Alert.query.get(alert_id)
    
    @staticmethod
    def get_active_alerts(db, limit=100):
        """Get all active alerts."""
        from models import Alert
        return Alert.query.filter(
            Alert.status.in_(['DETECTED', 'EVALUATING', 'VERIFIED'])
        ).order_by(Alert.created_at.desc()).limit(limit).all()
    
    @staticmethod
    def acknowledge_alert(db, alert_id):
        """Acknowledge an alert."""
        from models import Alert
        from datetime import datetime
        
        alert = Alert.query.get(alert_id)
        if alert:
            alert.status = 'EVALUATING'
            alert.acknowledged_at = datetime.utcnow()
            db.session.commit()
        
        return alert
    
    @staticmethod
    def resolve_alert(db, alert_id, resolution='VERIFIED'):
        """Resolve an alert."""
        from models import Alert
        from datetime import datetime
        
        alert = Alert.query.get(alert_id)
        if alert:
            alert.status = resolution  # VERIFIED or FALSE_POSITIVE
            alert.resolved_at = datetime.utcnow()
            db.session.commit()
        
        return alert
    
    @staticmethod
    def get_notification_channels(severity):
        """Get notification channels for severity level."""
        return AlertManager.SEVERITY_TO_ACTION.get(severity, ['log'])
    
    @staticmethod
    def send_notification(alert, channels):
        """Send notification via specified channels."""
        results = {}
        
        for channel in channels:
            if channel == 'email':
                results[channel] = AlertManager._send_email(alert)
            elif channel == 'sms':
                results[channel] = AlertManager._send_sms(alert)
            elif channel == 'dashboard':
                results[channel] = True  # Dashboard updates in real-time
            elif channel == 'alarm':
                results[channel] = AlertManager._trigger_alarm(alert)
            elif channel == 'log':
                results[channel] = True  # Always log
        
        return results
    
    @staticmethod
    def _send_email(alert):
        """Send email notification."""
        # In production, would use email service
        return True
    
    @staticmethod
    def _send_sms(alert):
        """Send SMS notification."""
        # In production, would use SMS service
        return True
    
    @staticmethod
    def _trigger_alarm(alert):
        """Trigger audio/visual alarm."""
        # In production, would trigger physical alarm
        return True
