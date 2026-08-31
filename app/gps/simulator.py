import random
import math
from datetime import datetime, timedelta
from geoalchemy2.elements import WKTElement

class GPSSimulator:
    """Simulates animal GPS movement with different modes."""
    
    def __init__(self, animal_id, lat, lon, speed_kmh=3.0):
        """Initialize GPS simulator."""
        self.animal_id = animal_id
        self.latitude = lat
        self.longitude = lon
        self.speed_kmh = speed_kmh
        self.heading = random.uniform(0, 360)
        self.altitude = 100
        
    def normal_movement(self):
        """Simulate normal forest movement."""
        # Random walk with slight bias
        self.heading += random.uniform(-30, 30)
        self.heading = self.heading % 360
        
        # Convert speed to degrees per second
        lat_change = (self.speed_kmh / 111.32) * (random.uniform(-1, 1) * 0.001)
        lon_change = (self.speed_kmh / (111.32 * math.cos(math.radians(self.latitude)))) * (random.uniform(-1, 1) * 0.001)
        
        self.latitude += lat_change
        self.longitude += lon_change
        
        return {
            'latitude': self.latitude,
            'longitude': self.longitude,
            'speed': self.speed_kmh + random.uniform(-0.5, 0.5),
            'heading': self.heading
        }
    
    def railway_approach(self):
        """Simulate approach toward railway."""
        # Move steadily toward railway (north-east direction assumed)
        self.heading = 45  # NE direction
        self.speed_kmh = 5.0  # Increased speed
        
        lat_change = (self.speed_kmh / 111.32) * 0.001
        lon_change = (self.speed_kmh / (111.32 * math.cos(math.radians(self.latitude)))) * 0.001
        
        self.latitude += lat_change
        self.longitude += lon_change
        
        return {
            'latitude': self.latitude,
            'longitude': self.longitude,
            'speed': self.speed_kmh,
            'heading': self.heading
        }
    
    def village_approach(self):
        """Simulate approach toward village."""
        # Move toward village (south direction assumed)
        self.heading = 180
        self.speed_kmh = 4.5
        
        lat_change = -(self.speed_kmh / 111.32) * 0.001
        lon_change = (self.speed_kmh / (111.32 * math.cos(math.radians(self.latitude)))) * (random.uniform(-0.5, 0.5) * 0.001)
        
        self.latitude += lat_change
        self.longitude += lon_change
        
        return {
            'latitude': self.latitude,
            'longitude': self.longitude,
            'speed': self.speed_kmh,
            'heading': self.heading
        }
    
    def get_gps_point(self, mode='normal'):
        """Get current GPS point based on mode."""
        if mode == 'railway':
            gps_point = self.railway_approach()
        elif mode == 'village':
            gps_point = self.village_approach()
        else:
            gps_point = self.normal_movement()
        
        gps_point['animal_id'] = self.animal_id
        gps_point['timestamp'] = datetime.utcnow()
        
        return gps_point
    
    def to_gps_event_dict(self, gps_point):
        """Convert GPS point to database format."""
        return {
            'animal_id': gps_point['animal_id'],
            'timestamp': gps_point['timestamp'],
            'latitude': gps_point['latitude'],
            'longitude': gps_point['longitude'],
            'speed': gps_point['speed'],
            'heading': gps_point['heading'],
            'location': WKTElement(
                f"POINT({gps_point['longitude']} {gps_point['latitude']})",
                srid=4326
            )
        }
