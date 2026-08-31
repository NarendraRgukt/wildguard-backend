# WildGuard Backend

Flask-based REST API for the WildGuard wildlife early-warning system.

## Features

- GPS telemetry ingestion and storage
- PostGIS geospatial calculations
- Railway and village geofencing
- Computer vision pipeline (MegaDetector + PyTorch-Wildlife)
- Movement anomaly detection
- Risk scoring engine
- AI investigation agent
- Alert management system

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export DATABASE_URL=postgresql://wildguard:wildguard123@localhost:5432/wildguard_db
export FLASK_ENV=development

# Run the server
python run.py
```

## API Documentation

See the main README for full API documentation.

## Project Structure

```
app/
├── models/          # Database models
├── routes/          # API routes
├── gps/            # GPS simulator
├── geo/            # Geofencing engine
├── vision/         # Computer vision
├── anomaly/        # Anomaly detection
├── risk/           # Risk engine
├── agent/          # Investigation agent
└── alerts/         # Alert management
```

## Dependencies

- Flask 3.0.0
- SQLAlchemy 3.1.1
- GeoAlchemy2 0.14.1
- PostGIS
- scikit-learn
- PyTorch
- PyTorch-Wildlife

## License

MIT
