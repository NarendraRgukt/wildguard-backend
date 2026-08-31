class RiskEngine:
    """Combines multiple signals to calculate risk scores."""
    
    # Risk weights
    RAILWAY_WEIGHTS = {
        'distance': 0.30,
        'direction': 0.25,
        'eta': 0.25,
        'anomaly': 0.10,
        'cctv': 0.10
    }
    
    VILLAGE_WEIGHTS = {
        'distance': 0.25,
        'direction': 0.25,
        'eta': 0.25,
        'anomaly': 0.15,
        'cctv': 0.10
    }
    
    # Thresholds for normalization
    RAILWAY_CRITICAL_DISTANCE_M = 500
    RAILWAY_ZONE_DISTANCE_M = 3000
    VILLAGE_CRITICAL_DISTANCE_M = 1000
    VILLAGE_ZONE_DISTANCE_M = 3000
    
    @staticmethod
    def calculate_railway_risk(distance_m, moving_toward_railway, eta_min, anomaly_detected, cctv_confirmed):
        """Calculate railway collision risk."""
        if distance_m > 10000:
            return 0  # No risk if far from railway
        
        # Distance component (0-100)
        if distance_m < RiskEngine.RAILWAY_CRITICAL_DISTANCE_M:
            distance_score = 100
        else:
            distance_score = 100 * (1 - (distance_m - RiskEngine.RAILWAY_CRITICAL_DISTANCE_M) / (RiskEngine.RAILWAY_ZONE_DISTANCE_M - RiskEngine.RAILWAY_CRITICAL_DISTANCE_M))
        
        distance_score = max(0, min(100, distance_score))
        
        # Direction component (0-100)
        direction_score = 100 if moving_toward_railway else 0
        
        # Direction uncertainty
        direction_score *= 0.8
        
        # ETA component (0-100)
        if eta_min is None:
            eta_score = 0
        elif eta_min < 5:
            eta_score = 100
        elif eta_min < 30:
            eta_score = 100 * (1 - (eta_min - 5) / 25)
        else:
            eta_score = 0
        
        eta_score = max(0, min(100, eta_score))
        
        # Anomaly component (0-100)
        anomaly_score = 100 if anomaly_detected else 20
        
        # CCTV component (0-100)
        cctv_score = 100 if cctv_confirmed else 60
        
        # Weighted combination
        risk_score = (
            RiskEngine.RAILWAY_WEIGHTS['distance'] * distance_score +
            RiskEngine.RAILWAY_WEIGHTS['direction'] * direction_score +
            RiskEngine.RAILWAY_WEIGHTS['eta'] * eta_score +
            RiskEngine.RAILWAY_WEIGHTS['anomaly'] * anomaly_score +
            RiskEngine.RAILWAY_WEIGHTS['cctv'] * cctv_score
        )
        
        return int(min(100, max(0, risk_score)))
    
    @staticmethod
    def calculate_village_risk(distance_m, moving_toward_village, eta_min, anomaly_detected, cctv_confirmed):
        """Calculate village conflict risk."""
        if distance_m > 10000:
            return 0  # No risk if far from village
        
        # Distance component (0-100)
        if distance_m < RiskEngine.VILLAGE_CRITICAL_DISTANCE_M:
            distance_score = 100
        else:
            distance_score = 100 * (1 - (distance_m - RiskEngine.VILLAGE_CRITICAL_DISTANCE_M) / (RiskEngine.VILLAGE_ZONE_DISTANCE_M - RiskEngine.VILLAGE_CRITICAL_DISTANCE_M))
        
        distance_score = max(0, min(100, distance_score))
        
        # Direction component (0-100)
        direction_score = 100 if moving_toward_village else 0
        direction_score *= 0.8
        
        # ETA component (0-100)
        if eta_min is None:
            eta_score = 0
        elif eta_min < 10:
            eta_score = 100
        elif eta_min < 45:
            eta_score = 100 * (1 - (eta_min - 10) / 35)
        else:
            eta_score = 0
        
        eta_score = max(0, min(100, eta_score))
        
        # Anomaly component (0-100)
        anomaly_score = 100 if anomaly_detected else 20
        
        # CCTV component (0-100)
        cctv_score = 100 if cctv_confirmed else 60
        
        # Weighted combination
        risk_score = (
            RiskEngine.VILLAGE_WEIGHTS['distance'] * distance_score +
            RiskEngine.VILLAGE_WEIGHTS['direction'] * direction_score +
            RiskEngine.VILLAGE_WEIGHTS['eta'] * eta_score +
            RiskEngine.VILLAGE_WEIGHTS['anomaly'] * anomaly_score +
            RiskEngine.VILLAGE_WEIGHTS['cctv'] * cctv_score
        )
        
        return int(min(100, max(0, risk_score)))
    
    @staticmethod
    def get_severity(risk_score):
        """Get severity level from risk score."""
        if risk_score >= 81:
            return 'CRITICAL'
        elif risk_score >= 61:
            return 'HIGH'
        elif risk_score >= 31:
            return 'MEDIUM'
        else:
            return 'LOW'
