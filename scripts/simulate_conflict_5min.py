#!/usr/bin/env python3
"""
WildGuard 5-Minute Conflict Simulation

This script simulates a 5-minute scenario where an animal approaches
a human settlement and triggers human-wildlife conflict alerts in real-time.

Real-time alerts are pushed to connected UI clients via SSE.

Usage:
    python simulate_conflict_5min.py
"""

import requests
import time
import math
from datetime import datetime

# Configuration
API_BASE_URL = "http://localhost:5000/api"

# Village location (target)
VILLAGE_LOCATION = (12.9700, 77.6050)
VILLAGE_RADIUS = 1500  # meters

# Starting position (far from village)
START_POSITION = (12.9850, 77.5800)  # 10km away

# Duration
SIMULATION_DURATION = 300  # 5 minutes = 300 seconds
UPDATE_INTERVAL = 2  # GPS update every 2 seconds

def calculate_distance(lat1, lon1, lat2, lon2):
    """Calculate distance in meters."""
    R = 6371000  # Earth's radius
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    
    a = math.sin(delta_phi/2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    
    return R * c


def move_towards_target(current_lat, current_lon, target_lat, target_lon, step_size=0.00005):
    """Move current position step_size degrees towards target."""
    lat_diff = target_lat - current_lat
    lon_diff = target_lon - current_lon
    distance = math.sqrt(lat_diff**2 + lon_diff**2)
    
    if distance < step_size:
        return target_lat, target_lon
    
    normalized_lat = (lat_diff / distance) * step_size
    normalized_lon = (lon_diff / distance) * step_size
    
    return current_lat + normalized_lat, current_lon + normalized_lon


def post_gps_data(animal_id, latitude, longitude, speed, heading):
    """Post GPS data to backend."""
    url = f"{API_BASE_URL}/gps"
    payload = {
        'animal_id': animal_id,
        'latitude': latitude,
        'longitude': longitude,
        'speed': speed,
        'heading': heading,
        'timestamp': datetime.utcnow().isoformat() + 'Z'
    }
    
    try:
        response = requests.post(url, json=payload, timeout=5)
        return response.status_code in [200, 202]
    except:
        return False


def create_animal(animal_code, species):
    """Create animal in backend."""
    url = f"{API_BASE_URL}/animals"
    payload = {
        'animal_code': animal_code,
        'species': species,
        'collar_id': f'COLLAR_{animal_code}',
        'status': 'ACTIVE'
    }
    
    try:
        response = requests.post(url, json=payload, timeout=5)
        if response.status_code in [200, 201]:
            return response.json()['id']
    except:
        pass
    
    return None


def main():
    """Main simulation."""
    print("\n" + "="*70)
    print("WildGuard 5-Minute Human-Wildlife Conflict Simulation")
    print("="*70)
    print(f"API Base URL: {API_BASE_URL}")
    print(f"Simulation Duration: 5 minutes = 300 seconds")
    print(f"Update Interval: {UPDATE_INTERVAL}s")
    print("="*70)
    
    # Check API
    try:
        requests.get(f"{API_BASE_URL}/animals", timeout=2)
        print("[OK] Backend is running\n")
    except:
        print("[ERROR] Cannot connect to backend")
        print("Please start backend: cd backend && python run.py\n")
        return
    
    # Create animal
    print("Creating animal...")
    animal_id = create_animal('TIG_CONFLICT_001', 'Tiger')
    if not animal_id:
        print("[ERROR] Failed to create animal")
        return
    print(f"[OK] Created Tiger (ID: {animal_id})\n")
    
    # Start position
    current_lat, current_lon = START_POSITION
    target_lat, target_lon = VILLAGE_LOCATION
    
    initial_distance = calculate_distance(current_lat, current_lon, target_lat, target_lon)
    print(f"Starting position: {current_lat:.4f}N, {current_lon:.4f}E")
    print(f"Target (Village): {target_lat:.4f}N, {target_lon:.4f}E")
    print(f"Initial distance: {initial_distance:.0f}m\n")
    
    print("Simulation starting...")
    print("-" * 70)
    print("Watch the dashboard at http://localhost:3000")
    print("Alerts will appear in real-time as tiger approaches village!")
    print("-" * 70 + "\n")
    
    start_time = time.time()
    update_count = 0
    
    try:
        while True:
            elapsed = time.time() - start_time
            
            if elapsed > SIMULATION_DURATION:
                break
            
            # Move towards target
            current_lat, current_lon = move_towards_target(
                current_lat, current_lon,
                target_lat, target_lon,
                step_size=0.00008  # ~8 meters
            )
            
            # Calculate current distance
            distance = calculate_distance(
                current_lat, current_lon,
                target_lat, target_lon
            )
            
            # Calculate speed (km/h)
            speed = 5.5 + (distance / initial_distance) * -2  # Speeds up as approaches
            
            # Calculate heading towards target
            lat_diff = target_lat - current_lat
            lon_diff = target_lon - current_lon
            heading = math.degrees(math.atan2(lon_diff, lat_diff))
            if heading < 0:
                heading += 360
            
            # Post GPS
            posted = post_gps_data(animal_id, current_lat, current_lon, speed, heading)
            if posted:
                update_count += 1
            
            # Status
            remaining = SIMULATION_DURATION - elapsed
            progress = int((elapsed / SIMULATION_DURATION) * 50)
            bar = "█" * progress + "░" * (50 - progress)
            
            # Alert level
            if distance < VILLAGE_RADIUS:
                alert_level = "[CRITICAL] CONFLICT RISK"
            elif distance < VILLAGE_RADIUS * 1.5:
                alert_level = "[HIGH] HIGH RISK"
            elif distance < VILLAGE_RADIUS * 2:
                alert_level = "[MEDIUM] MEDIUM RISK"
            else:
                alert_level = "[APPROACHING] APPROACHING"
            
            print(f"\r[{bar}] {remaining:.0f}s | Distance: {distance:.0f}m | {alert_level}", end='', flush=True)
            
            time.sleep(UPDATE_INTERVAL)
    
    except KeyboardInterrupt:
        print("\n\n✓ Simulation stopped by user")
    
    print("\n\n" + "="*70)
    print("Simulation Complete!")
    print("="*70)
    print(f"Duration: {elapsed:.1f} seconds")
    print(f"GPS Updates Posted: {update_count}")
    print(f"Final Distance from Village: {distance:.0f}m")
    print("\nResults on Dashboard:")
    print("   http://localhost:3000")
    print("\nWhat you should see:")
    print("   * Tiger moving on map from southeast to village")
    print("   * Alerts appearing as distance decreases")
    print("   * Risk scores increasing (0→100)")
    print("   * Severity escalating (LOW→CRITICAL)")
    print("   * Investigation summaries with recommendations\n")


if __name__ == '__main__':
    main()
