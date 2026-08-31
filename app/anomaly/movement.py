import numpy as np
from sklearn.ensemble import IsolationForest
from datetime import datetime, timedelta

class AnomalyDetector:
    """Detects anomalies in animal movement patterns."""
    
    def __init__(self, contamination=0.1):
        """Initialize anomaly detector."""
        self.contamination = contamination
        self.model = IsolationForest(contamination=contamination, random_state=42)
        self.fitted = False
        self.feature_means = {}
        self.feature_stds = {}
    
    def extract_features(self, gps_history, current_point):
        """Extract features from GPS history and current point."""
        features = {}
        
        if len(gps_history) < 2:
            return None  # Not enough data
        
        # Basic features
        current_speed = current_point.get('speed', 0)
        current_heading = current_point.get('heading', 0)
        
        # Historical features
        speeds = [p.get('speed', 0) for p in gps_history[-10:]]
        headings = [p.get('heading', 0) for p in gps_history[-10:]]
        
        avg_speed = np.mean(speeds) if speeds else 0
        std_speed = np.std(speeds) if speeds else 0
        max_speed = np.max(speeds) if speeds else 0
        
        # Heading changes
        heading_changes = []
        for i in range(1, len(headings)):
            change = abs(headings[i] - headings[i-1])
            if change > 180:
                change = 360 - change
            heading_changes.append(change)
        
        avg_heading_change = np.mean(heading_changes) if heading_changes else 0
        
        # Time-based features
        hour_of_day = datetime.utcnow().hour
        
        features = {
            'current_speed': current_speed,
            'avg_speed': avg_speed,
            'std_speed': std_speed,
            'max_speed_ratio': (current_speed / max_speed) if max_speed > 0 else 0,
            'heading_change': abs(current_heading - headings[-1]) if headings else 0,
            'avg_heading_change': avg_heading_change,
            'hour_of_day': hour_of_day,
            'speed_change': current_speed - avg_speed if avg_speed > 0 else 0
        }
        
        return features
    
    def train(self, historical_data):
        """Train anomaly detector on historical data."""
        if len(historical_data) < 10:
            return False
        
        X = []
        for data_point in historical_data:
            features = data_point
            X.append([
                features.get('current_speed', 0),
                features.get('avg_speed', 0),
                features.get('std_speed', 0),
                features.get('max_speed_ratio', 0),
                features.get('heading_change', 0),
                features.get('avg_heading_change', 0),
                features.get('hour_of_day', 0),
                features.get('speed_change', 0)
            ])
        
        X = np.array(X)
        self.model.fit(X)
        self.fitted = True
        
        # Store normalization parameters
        self.feature_means = np.mean(X, axis=0)
        self.feature_stds = np.std(X, axis=0)
        
        return True
    
    def predict(self, features):
        """Predict if movement is anomalous."""
        if not self.fitted:
            return {'is_anomaly': False, 'score': 0}
        
        if features is None:
            return {'is_anomaly': False, 'score': 0}
        
        X = np.array([[
            features.get('current_speed', 0),
            features.get('avg_speed', 0),
            features.get('std_speed', 0),
            features.get('max_speed_ratio', 0),
            features.get('heading_change', 0),
            features.get('avg_heading_change', 0),
            features.get('hour_of_day', 0),
            features.get('speed_change', 0)
        ]])
        
        prediction = self.model.predict(X)[0]
        anomaly_score = -self.model.score_samples(X)[0]
        
        return {
            'is_anomaly': prediction == -1,
            'score': float(anomaly_score),
            'normalized_score': float(min(100, anomaly_score * 10))
        }
