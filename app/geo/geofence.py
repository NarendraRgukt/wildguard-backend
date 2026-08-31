from sqlalchemy import func, text
from geoalchemy2 import Geography
from geoalchemy2.elements import WKTElement
import math

class GeofenceService:
    """Service for geofence operations and proximity calculations."""
    
    @staticmethod
    def create_point_buffer(latitude, longitude, buffer_m, db):
        """Create a buffer geometry around a point."""
        # Use PostGIS ST_Buffer (converts to meters using ST_Transform)
        return text(f"""
            SELECT ST_Buffer(
                ST_SetSRID(ST_Point({longitude}, {latitude}), 4326)::geography,
                {buffer_m}
            )::geography
        """)
    
    @staticmethod
    def create_village_geofence(name, latitude, longitude, buffer_m=2000):
        """Create a circular village geofence."""
        # Create a buffer around the village center point
        geometry = WKTElement(
            f"POLYGON(({_create_circular_polygon(latitude, longitude, buffer_m)}))",
            srid=4326
        )
        return {
            'name': name,
            'type': 'VILLAGE',
            'geometry': geometry,
            'risk_level': 'HIGH'
        }
    
    @staticmethod
    def create_railway_geofence(name, start_lat, start_lon, end_lat, end_lon, buffer_m=1000):
        """Create a railway corridor geofence."""
        # Create a buffer around a line
        geometry = WKTElement(
            f"LINESTRING({start_lon} {start_lat}, {end_lon} {end_lat})",
            srid=4326
        )
        return {
            'name': name,
            'type': 'RAILWAY',
            'geometry': geometry,
            'risk_level': 'CRITICAL'
        }
    
    @staticmethod
    def calculate_distance(lat1, lon1, lat2, lon2):
        """Calculate distance between two points using Haversine formula."""
        R = 6371000  # Earth radius in meters
        
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)
        
        a = math.sin(delta_lat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        
        return R * c
    
    @staticmethod
    def calculate_bearing(lat1, lon1, lat2, lon2):
        """Calculate bearing from point 1 to point 2."""
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lon = math.radians(lon2 - lon1)
        
        x = math.sin(delta_lon) * math.cos(lat2_rad)
        y = math.cos(lat1_rad) * math.sin(lat2_rad) - math.sin(lat1_rad) * math.cos(lat2_rad) * math.cos(delta_lon)
        
        bearing = math.degrees(math.atan2(x, y))
        return (bearing + 360) % 360
    
    @staticmethod
    def is_moving_toward(current_bearing, target_bearing, tolerance=45):
        """Check if current bearing is toward target."""
        delta = abs(current_bearing - target_bearing)
        if delta > 180:
            delta = 360 - delta
        return delta <= tolerance
    
    @staticmethod
    def calculate_eta(distance_m, speed_kmh):
        """Calculate estimated time of arrival in minutes."""
        if speed_kmh == 0:
            return None
        speed_ms = speed_kmh / 3.6
        time_seconds = distance_m / speed_ms
        return time_seconds / 60

def _create_circular_polygon(center_lat, center_lon, radius_m, points=32):
    """Create a circular polygon around a center point."""
    import math
    
    coords = []
    R = 6371000  # Earth radius in meters
    
    for i in range(points):
        angle = 2 * math.pi * i / points
        lat_offset = math.sin(angle) * (radius_m / R)
        lon_offset = math.cos(angle) * (radius_m / (R * math.cos(math.radians(center_lat))))
        
        lat = center_lat + math.degrees(lat_offset)
        lon = center_lon + math.degrees(lon_offset)
        coords.append(f"{lon} {lat}")
    
    # Close the polygon
    coords.append(coords[0])
    return ", ".join(coords)
