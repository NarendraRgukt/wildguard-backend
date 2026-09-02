# Sample test data generator
import requests
import json
from datetime import datetime, timedelta
import random

API_URL = "http://localhost:5000/api"

def create_sample_animals():
    """Create sample animals in the database."""
    animals = [
        {
            "animal_code": "ELE_001",
            "species": "Elephant",
            "collar_id": "COL_001",
            "status": "ACTIVE"
        },
        {
            "animal_code": "ELE_002",
            "species": "Elephant",
            "collar_id": "COL_002",
            "status": "ACTIVE"
        },
        {
            "animal_code": "TIG_001",
            "species": "Tiger",
            "collar_id": "COL_003",
            "status": "ACTIVE"
        }
    ]
    
    for animal in animals:
        try:
            response = requests.post(f"{API_URL}/animals", json=animal)
            print(f"Created animal: {response.json()}")
        except Exception as e:
            print(f"Error creating animal: {e}")

def generate_gps_data():
    """Generate sample GPS data for animals."""
    animals = [
        {"animal_id": "ELE_001", "lat": 12.3456, "lon": 76.5432},
        {"animal_id": "ELE_002", "lat": 12.3500, "lon": 76.5500},
        {"animal_id": "TIG_001", "lat": 12.3300, "lon": 76.5300},
    ]
    
    for i in range(20):
        for animal in animals:
            gps_data = {
                "animal_id": animal["animal_id"],
                "latitude": animal["lat"] + (random.random() - 0.5) * 0.01,
                "longitude": animal["lon"] + (random.random() - 0.5) * 0.01,
                "speed": random.uniform(0, 10),
                "heading": random.uniform(0, 360),
                "timestamp": (datetime.utcnow() - timedelta(minutes=20-i)).isoformat()
            }
            
            try:
                response = requests.post(f"{API_URL}/gps", json=gps_data)
                print(f"Generated GPS data: {animal['animal_id']}")
            except Exception as e:
                print(f"Error generating GPS data: {e}")

if __name__ == "__main__":
    print("Creating sample animals...")
    create_sample_animals()
    
    print("\nGenerating GPS data...")
    generate_gps_data()
    
    print("\nDone!")
