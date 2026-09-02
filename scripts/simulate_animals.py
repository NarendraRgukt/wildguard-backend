#!/usr/bin/env python3
"""
WildGuard Comprehensive Data Simulator

This script simulates:
- Animal GPS positions (normal, railway approach, village approach)
- CCTV/camera trap detections
- Human-wildlife conflict detection
- Automated alert generation

Run this to generate live data for the dashboard.

Usage:
    python simulate_animals.py
"""

import requests
import time
import random
import sys
import math
import os
from datetime import datetime
from pathlib import Path

# BACKEND_DIR is set by the backend when the simulator runs in Docker.
# The script is bundled at backend/scripts/, so its parent directory is backend/.
backend_dir = Path(os.getenv('BACKEND_DIR', str(Path(__file__).resolve().parents[1])))
sys.path.insert(0, str(backend_dir))

from app.gps.simulator import GPSSimulator

# Configuration
API_BASE_URL = os.getenv('API_BASE_URL', "http://localhost:5000/api")
UPDATE_INTERVAL = 3  # seconds between updates

# Geofence locations and radii
RAILWAY_LOCATION = (12.9750, 77.5900)
RAILWAY_RADIUS = 1000  # meters

VILLAGE_LOCATION = (12.9700, 77.6050)
VILLAGE_RADIUS = 1500  # meters

# Camera locations
CAMERA_LOCATIONS = [
    {
        'camera_id': 'CAM_01',
        'name': 'Railway Zone Camera',
        'latitude': 12.9740,
        'longitude': 77.5920
    },
    {
        'camera_id': 'CAM_02',
        'name': 'Village Zone Camera',
        'latitude': 12.9690,
        'longitude': 77.6040
    },
    {
        'camera_id': 'CAM_03',
        'name': 'Forest Zone Camera',
        'latitude': 12.9800,
        'longitude': 77.5850
    }
]

# Animal starting positions (latitude, longitude)
ANIMALS = [
    {
        'animal_id': 'ELE_001',
        'animal_code': 'ELE_001',
        'species': 'Elephant',
        'collar_id': 'COLLAR_ELE_001',
        'latitude': 12.9716,
        'longitude': 77.5946
    },
    {
        'animal_id': 'TIG_001',
        'animal_code': 'TIG_001',
        'species': 'Tiger',
        'collar_id': 'COLLAR_TIG_001',
        'latitude': 12.9750,
        'longitude': 77.5900
    },
    {
        'animal_id': 'LEO_001',
        'animal_code': 'LEO_001',
        'species': 'Leopard',
        'collar_id': 'COLLAR_LEO_001',
        'latitude': 12.9680,
        'longitude': 77.6000
    }
]

MOVEMENT_MODES = ['normal', 'normal', 'normal', 'railway', 'village']


def calculate_distance(lat1, lon1, lat2, lon2):
    """Calculate distance in meters between two coordinates."""
    R = 6371000  # Earth's radius in meters
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    
    a = math.sin(delta_phi/2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    distance = R * c
    
    return distance


def create_animal(animal_data):
    """Create an animal in the backend."""
    url = f"{API_BASE_URL}/animals"
    payload = {
        'animal_code': animal_data['animal_code'],
        'species': animal_data['species'],
        'collar_id': animal_data.get('collar_id'),
        'status': 'ACTIVE'
    }
    
    try:
        response = requests.post(url, json=payload, timeout=5)
        if response.status_code == 201:
            print(f"âœ“ Created animal: {animal_data['animal_code']} ({animal_data['species']})")
            return response.json()['id']
        elif response.status_code == 400:
            # Already exists, fetch it
            list_url = f"{API_BASE_URL}/animals"
            list_response = requests.get(list_url, timeout=5)
            animals = list_response.json().get('animals', [])
            for a in animals:
                if a['animal_code'] == animal_data['animal_code']:
                    print(f"âœ“ Animal exists: {animal_data['animal_code']}")
                    return a['id']
        else:
            print(f"âœ— Failed to create {animal_data['animal_code']}: {response.text}")
            return None
    except Exception as e:
        print(f"âœ— Error creating animal: {e}")
        return None


def post_gps_data(animal_id, gps_point):
    """Post GPS data to the backend."""
    url = f"{API_BASE_URL}/gps"
    payload = {
        'animal_id': animal_id,
        'latitude': gps_point['latitude'],
        'longitude': gps_point['longitude'],
        'speed': gps_point['speed'],
        'heading': gps_point['heading'],
        'timestamp': gps_point['timestamp'].isoformat() + 'Z'
    }
    
    try:
        response = requests.post(url, json=payload, timeout=5)
        return response.status_code in [200, 202]
    except Exception as e:
        return False


def simulate_camera_detection(animal_id, species, latitude, longitude, confidence=0.85):
    """Simulate a camera trap detection."""
    url = f"{API_BASE_URL}/camera-events"
    
    # Find closest camera
    closest_camera = None
    closest_distance = float('inf')
    
    for camera in CAMERA_LOCATIONS:
        dist = calculate_distance(camera['latitude'], camera['longitude'], latitude, longitude)
        if dist < closest_distance:
            closest_distance = dist
            closest_camera = camera
    
    # Only create detection if within 500m of a camera
    if closest_distance > 500:
        return False
    
    payload = {
        'camera_id': closest_camera['camera_id'],
        'timestamp': datetime.utcnow().isoformat() + 'Z',
        'object_type': 'animal',
        'species': species,
        'confidence': confidence,
        'latitude': latitude,
        'longitude': longitude,
        'image_path': f"camera_{closest_camera['camera_id']}/frame_{int(time.time())}.jpg"
    }
    
    try:
        response = requests.post(url, json=payload, timeout=5)
        return response.status_code in [200, 202]
    except Exception as e:
        return False


def create_alert(animal_id, species, latitude, longitude, threat_type, risk_score, cctv_confirmed=False):
    """Create an alert based on detected threat."""
    url = f"{API_BASE_URL}/alerts"
    
    severity_map = {
        'LOW': 'LOW',
        'MEDIUM': 'MEDIUM',
        'HIGH': 'HIGH',
        'CRITICAL': 'CRITICAL'
    }
    
    # Determine severity based on risk score
    if risk_score >= 80:
        severity = severity_map['CRITICAL']
    elif risk_score >= 60:
        severity = severity_map['HIGH']
    elif risk_score >= 40:
        severity = severity_map['MEDIUM']
    else:
        severity = severity_map['LOW']
    
    # Create description based on threat type
    descriptions = {
        'RAILWAY': f"{species} {animal_id} approaching railway zone. Distance to track: {risk_score}m. Action: Immediate notification to railway authorities.",
        'VILLAGE': f"{species} {animal_id} approaching human settlement. Potential human-wildlife conflict risk. Action: Alert forest department for protective measures.",
        'HUMAN_CONFLICT': f"âš ï¸ CRITICAL: {species} {animal_id} detected near village. High risk of human injury or livestock predation. Action: Immediate response required."
    }
    
    payload = {
        'animal_id': animal_id,
        'species': species,
        'threat_type': threat_type,
        'severity': severity,
        'risk_score': risk_score,
        'description': descriptions.get(threat_type, f'{species} detected in restricted zone'),
        'gps_location': {'latitude': latitude, 'longitude': longitude},
        'cctv_confirmed': cctv_confirmed,
        'anomaly_detected': True,
        'investigation_summary': f'Automated detection: {threat_type} risk detected for {species} {animal_id}. Risk score: {risk_score}/100. CCTV confirmation: {"Yes" if cctv_confirmed else "No"}. Recommendation: Verify location and issue appropriate alert to field teams.',
        'status': 'DETECTED'
    }
    
    try:
        response = requests.post(url, json=payload, timeout=5)
        return response.status_code in [200, 201]
    except Exception as e:
        return False


def check_geofence_proximity(latitude, longitude, geofence_location, geofence_radius):
    """Check if position is within geofence radius."""
    distance = calculate_distance(
        latitude, longitude,
        geofence_location[0], geofence_location[1]
    )
    
    return distance, distance <= geofence_radius


def simulate_animals():
    """Main simulation loop."""
    print("\n" + "="*70)
    print("WildGuard Comprehensive Data Simulator")
    print("GPS Telemetry + CCTV Detection + Alert Generation")
    print("="*70)
    print(f"API Base URL: {API_BASE_URL}")
    print(f"Update interval: {UPDATE_INTERVAL}s")
    print(f"Monitoring {len(ANIMALS)} animals across {len(CAMERA_LOCATIONS)} cameras")
    print("="*70 + "\n")
    
    # Check if API is available
    try:
        response = requests.get(f"{API_BASE_URL}/animals", timeout=2)
        print("âœ“ Backend API is running\n")
    except Exception as e:
        print(f"âœ— Cannot connect to backend API at {API_BASE_URL}")
        print(f"  Error: {e}")
        print("\nPlease make sure the backend is running:")
        print("  cd backend && python run.py\n")
        return
    
    # Create animals
    print("Setting up animals...")
    simulators = {}
    
    for animal_data in ANIMALS:
        animal_id = create_animal(animal_data)
        if animal_id:
            simulator = GPSSimulator(
                animal_id,
                animal_data['latitude'],
                animal_data['longitude'],
                speed_kmh=random.uniform(2, 6)
            )
            simulators[animal_data['animal_code']] = {
                'simulator': simulator,
                'animal_id': animal_id,
                'species': animal_data['species'],
                'mode': 'normal',
                'mode_change_counter': random.randint(30, 100),
                'cctv_detection_counter': 0,
                'alert_cooldown': 0
            }
    
    print(f"\nâœ“ Setup complete - monitoring {len(simulators)} animals")
    print("\nSimulation started. Press Ctrl+C to stop.\n")
    print("Data being generated:")
    print("  â€¢ GPS positions every {}s".format(UPDATE_INTERVAL))
    print("  â€¢ CCTV detections when near cameras")
    print("  â€¢ Alerts for railway/village proximity and human conflicts\n")
    print("-" * 70)
    
    iteration = 0
    
    try:
        while True:
            iteration += 1
            posted_gps = 0
            posted_cctv = 0
            posted_alerts = 0
            
            for animal_code, data in simulators.items():
                # Change mode periodically
                data['mode_change_counter'] -= 1
                if data['mode_change_counter'] <= 0:
                    data['mode'] = random.choice(MOVEMENT_MODES)
                    data['mode_change_counter'] = random.randint(30, 100)
                
                # Generate GPS point
                gps_point = data['simulator'].get_gps_point(mode=data['mode'])
                
                # Post GPS
                if post_gps_data(data['animal_id'], gps_point):
                    posted_gps += 1
                
                lat = gps_point['latitude']
                lon = gps_point['longitude']
                
                # Check railway proximity
                railway_dist, railway_breach = check_geofence_proximity(
                    lat, lon, RAILWAY_LOCATION, RAILWAY_RADIUS
                )
                
                # Check village proximity
                village_dist, village_breach = check_geofence_proximity(
                    lat, lon, VILLAGE_LOCATION, VILLAGE_RADIUS
                )
                
                # Simulate CCTV detection (random chance)
                cctv_detected = False
                if random.random() < 0.15:  # 15% chance per update
                    if simulate_camera_detection(
                        data['animal_id'],
                        data['species'],
                        lat, lon,
                        confidence=random.uniform(0.80, 0.99)
                    ):
                        posted_cctv += 1
                        cctv_detected = True
                
                # Alert generation (with cooldown to avoid spam)
                data['alert_cooldown'] = max(0, data['alert_cooldown'] - 1)
                
                if data['alert_cooldown'] == 0:
                    alert_created = False
                    
                    # Railway conflict alert
                    if railway_breach:
                        risk_score = max(60, 100 - int(railway_dist / 10))
                        if create_alert(
                            data['animal_id'],
                            data['species'],
                            lat, lon,
                            'RAILWAY',
                            risk_score,
                            cctv_confirmed=cctv_detected
                        ):
                            posted_alerts += 1
                            alert_created = True
                    
                    # Village/human conflict alert
                    elif village_breach:
                        risk_score = max(50, 90 - int(village_dist / 20))
                        if create_alert(
                            data['animal_id'],
                            data['species'],
                            lat, lon,
                            'HUMAN_CONFLICT',
                            risk_score,
                            cctv_confirmed=cctv_detected
                        ):
                            posted_alerts += 1
                            alert_created = True
                    
                    if alert_created:
                        data['alert_cooldown'] = 100  # 5 minute cooldown (100 updates at 3s each)
            
            # Status update
            status_str = f"[{iteration:05d}] GPS: {posted_gps} | CCTV: {posted_cctv} | Alerts: {posted_alerts}"
            print(f"\r{status_str:<50}", end='', flush=True)
            
            time.sleep(UPDATE_INTERVAL)
    
    except KeyboardInterrupt:
        print("\n\n" + "="*70)
        print("âœ“ Simulation stopped by user")
        print("="*70)
        print("\nðŸ“Š Dashboard Access:")
        print("   â†’ Open http://localhost:3000 in your browser")
        print("\nâœ¨ What you can see:")
        print("   â€¢ Live animal positions on the map")
        print("   â€¢ Animal details (species, speed, direction)")
        print("   â€¢ Real-time alerts (railway & human-wildlife conflicts)")
        print("   â€¢ CCTV detection confirmations")
        print("   â€¢ Risk scores and investigation summaries")
        print("   â€¢ Alert acknowledgment capabilities\n")


if __name__ == '__main__':
    simulate_animals()
