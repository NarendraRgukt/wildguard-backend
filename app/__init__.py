from flask import Flask, jsonify, request
import sys
import os
import subprocess
import threading
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from extensions import db, migrate, cors, init_extensions
    from config import config
    HAS_EXTENSIONS = True
except ImportError as e:
    HAS_EXTENSIONS = False
    print(f"Warning: Could not import extensions: {e}")

# Demo data storage (in-memory for demo purposes without database)
_demo_animals = {}
_demo_gps_events = {}
_demo_camera_events = []
_demo_alerts = {}
_alert_subscribers = []  # For real-time SSE
_simulation_process = None
_simulation_lock = threading.Lock()


def _simulation_script_path():
    """Return the simulator bundled with the backend service."""
    return Path(__file__).resolve().parents[1] / 'scripts' / 'simulate_animals.py'
def create_app(config_name=None):
    """Application factory function."""
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')
    
    app = Flask(__name__)
    
    # Load configuration if available
    if HAS_EXTENSIONS:
        app.config.from_object(config[config_name])
        init_extensions(app)
    else:
        app.config['DEBUG'] = True
        # Enable CORS manually if extensions not available
        from flask_cors import CORS
        CORS(app)
    
    # Health check endpoint
    @app.route('/health', methods=['GET'])
    def health():
        return jsonify({'status': 'healthy', 'message': 'WildGuard Backend API is running'}), 200

    @app.route('/api/simulation', methods=['GET'])
    def simulation_status():
        with _simulation_lock:
            running = _simulation_process is not None and _simulation_process.poll() is None
        return jsonify({'running': running}), 200

    @app.route('/api/simulation/start', methods=['POST'])
    def start_simulation():
        global _simulation_process
        with _simulation_lock:
            if _simulation_process is not None and _simulation_process.poll() is None:
                return jsonify({'running': True, 'message': 'Simulation is already running'}), 200
            script_path = _simulation_script_path()
            if not script_path.exists():
                return jsonify({'error': 'Bundled simulator script was not found'}), 500
            environment = os.environ.copy()
            environment['API_BASE_URL'] = request.host_url.rstrip('/') + '/api'
            environment['BACKEND_DIR'] = str(Path(__file__).resolve().parents[2])
            try:
                _simulation_process = subprocess.Popen([sys.executable, str(script_path)], cwd=str(script_path.parent), env=environment, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except OSError as error:
                return jsonify({'error': f'Unable to start simulation: {error}'}), 500
        return jsonify({'running': True, 'message': 'Animal simulation started'}), 202
    # ==================== ANIMALS ENDPOINTS ====================
    
    @app.route('/api/animals', methods=['GET'])
    def list_animals():
        """List all animals."""
        try:
            status = request.args.get('status')
            species = request.args.get('species')

            animals_list = list(_demo_animals.values())

            if status:
                animals_list = [a for a in animals_list if a.get('status') == status]

            if species:
                # case-insensitive match
                animals_list = [a for a in animals_list if (a.get('species') or '').lower() == species.lower()]

            return jsonify({
                'count': len(animals_list),
                'animals': animals_list
            }), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/animals/grouped', methods=['GET'])
    def grouped_animals():
        """Return animals grouped by species."""
        try:
            animals_list = list(_demo_animals.values())
            grouped = {}
            for a in animals_list:
                key = a.get('species') or 'Unknown'
                grouped.setdefault(key, []).append(a)

            return jsonify({
                'groups': grouped,
                'count': len(animals_list)
            }), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/animals', methods=['POST'])
    def create_animal():
        """Create a new animal."""
        try:
            import uuid
            
            data = request.get_json()
            animal_id = str(uuid.uuid4())
            
            animal = {
                'id': animal_id,
                'animal_code': data.get('animal_code'),
                'species': data.get('species'),
                'collar_id': data.get('collar_id'),
                'status': data.get('status', 'ACTIVE'),
                'created_at': __import__('datetime').datetime.utcnow().isoformat()
            }
            
            _demo_animals[animal_id] = animal
            return jsonify(animal), 201
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/animals/<animal_id>', methods=['GET'])
    def get_animal(animal_id):
        """Get animal details."""
        try:
            animal = _demo_animals.get(animal_id)
            if not animal:
                return jsonify({'error': 'Animal not found'}), 404
            return jsonify(animal), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    # ==================== GPS ENDPOINTS ====================
    
    @app.route('/api/gps', methods=['POST'])
    def ingest_gps():
        """Ingest GPS data."""
        try:
            from flask import request
            import uuid
            
            data = request.get_json()
            gps_id = str(uuid.uuid4())
            
            gps_event = {
                'id': gps_id,
                'animal_id': data.get('animal_id'),
                'latitude': data.get('latitude'),
                'longitude': data.get('longitude'),
                'speed': data.get('speed'),
                'heading': data.get('heading'),
                'timestamp': data.get('timestamp')
            }
            
            animal_id = data.get('animal_id')
            if animal_id not in _demo_gps_events:
                _demo_gps_events[animal_id] = []
            
            _demo_gps_events[animal_id].append(gps_event)
            
            return jsonify({
                'status': 'accepted',
                'event_id': gps_id,
                'animal_id': animal_id
            }), 202
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/gps/animal/<animal_id>/latest', methods=['GET'])
    def get_latest_gps(animal_id):
        """Get latest GPS for animal."""
        try:
            events = _demo_gps_events.get(animal_id, [])
            if not events:
                return jsonify({'error': 'No GPS data found'}), 404
            
            latest = events[-1]
            return jsonify(latest), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/gps/animal/<animal_id>/history', methods=['GET'])
    def get_gps_history(animal_id):
        """Get GPS history for animal."""
        try:
            from flask import request
            import datetime

            # Query params: limit (int), start (ISO datetime), end (ISO datetime)
            limit = request.args.get('limit', 100, type=int)
            start = request.args.get('start')
            end = request.args.get('end')

            events = list(_demo_gps_events.get(animal_id, []))

            def parse_iso(s: str):
                if not s:
                    return None
                try:
                    # strip trailing Z if present
                    s2 = s.rstrip('Z')
                    return datetime.datetime.fromisoformat(s2)
                except Exception:
                    try:
                        # fallback: attempt to parse as naive datetime
                        return datetime.datetime.strptime(s, '%Y-%m-%dT%H:%M:%S')
                    except Exception:
                        return None

            start_dt = parse_iso(start)
            end_dt = parse_iso(end)

            if start_dt or end_dt:
                filtered = []
                for e in events:
                    ts = e.get('timestamp')
                    if not ts:
                        continue
                    t = None
                    try:
                        t = datetime.datetime.fromisoformat(ts.rstrip('Z'))
                    except Exception:
                        try:
                            t = datetime.datetime.strptime(ts, '%Y-%m-%dT%H:%M:%S')
                        except Exception:
                            continue

                    if start_dt and t < start_dt:
                        continue
                    if end_dt and t > end_dt:
                        continue
                    filtered.append(e)

                events = filtered

            history = events[-limit:] if limit else events

            return jsonify({
                'animal_id': animal_id,
                'events': history
            }), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    # ==================== CAMERA EVENTS ENDPOINTS ====================
    
    @app.route('/api/camera-events', methods=['POST'])
    def ingest_camera_event():
        """Ingest camera/CCTV event data."""
        try:
            from flask import request
            import uuid
            
            data = request.get_json()
            camera_id = str(uuid.uuid4())
            
            camera_event = {
                'id': camera_id,
                'camera_id': data.get('camera_id'),
                'timestamp': data.get('timestamp'),
                'object_type': data.get('object_type'),  # animal, human, vehicle
                'species': data.get('species'),
                'confidence': data.get('confidence'),
                'latitude': data.get('latitude'),
                'longitude': data.get('longitude'),
                'image_path': data.get('image_path')
            }
            
            # Store camera event
            if 'camera_events' not in __import__('sys').modules[__name__].__dict__:
                globals()['_demo_camera_events'] = []
            globals()['_demo_camera_events'].append(camera_event)
            
            return jsonify({
                'status': 'accepted',
                'event_id': camera_id,
                'camera_id': data.get('camera_id')
            }), 202
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/camera-events', methods=['GET'])
    def list_camera_events():
        """List all camera events."""
        try:
            camera_events = globals().get('_demo_camera_events', [])
            return jsonify({
                'count': len(camera_events),
                'events': camera_events
            }), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    # ==================== ALERTS ENDPOINTS ====================
    
    @app.route('/api/alerts', methods=['GET'])
    def list_alerts():
        """List all alerts."""
        try:
            status = request.args.get('status')
            alerts_list = list(_demo_alerts.values())
            
            if status:
                alerts_list = [a for a in alerts_list if a.get('status') == status]
            
            return jsonify({
                'count': len(alerts_list),
                'alerts': alerts_list
            }), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/alerts/<alert_id>', methods=['GET'])
    def get_alert(alert_id):
        """Get alert details."""
        try:
            alert = _demo_alerts.get(alert_id)
            if not alert:
                return jsonify({'error': 'Alert not found'}), 404
            return jsonify(alert), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/alerts', methods=['POST'])
    def create_alert():
        """Create a new alert."""
        try:
            import uuid
            
            data = request.get_json()
            alert_id = str(uuid.uuid4())
            
            alert = {
                'id': alert_id,
                'animal_id': data.get('animal_id'),
                'species': data.get('species'),
                'threat_type': data.get('threat_type'),  # RAILWAY, VILLAGE, HUMAN_CONFLICT
                'severity': data.get('severity', 'MEDIUM'),  # LOW, MEDIUM, HIGH, CRITICAL
                'risk_score': data.get('risk_score', 0),
                'description': data.get('description'),
                'investigation_summary': data.get('investigation_summary'),
                'gps_location': data.get('gps_location'),
                'cctv_confirmed': data.get('cctv_confirmed', False),
                'anomaly_detected': data.get('anomaly_detected', False),
                'status': data.get('status', 'DETECTED'),
                'created_at': __import__('datetime').datetime.utcnow().isoformat()
            }
            
            _demo_alerts[alert_id] = alert
            
            # Broadcast to SSE clients
            for client_queue in _alert_subscribers:
                try:
                    client_queue.put(alert)
                except:
                    pass
            
            return jsonify(alert), 201
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/alerts/<alert_id>/acknowledge', methods=['POST'])
    def acknowledge_alert(alert_id):
        """Acknowledge an alert."""
        try:
            if alert_id not in _demo_alerts:
                return jsonify({'error': 'Alert not found'}), 404
            
            _demo_alerts[alert_id]['status'] = 'ACKNOWLEDGED'
            return jsonify(_demo_alerts[alert_id]), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    # ==================== REAL-TIME ALERTS SSE ====================
    
    @app.route('/api/alerts/stream', methods=['GET'])
    def stream_alerts():
        """Stream alerts in real-time using Server-Sent Events."""
        from queue import Queue
        
        alert_queue = Queue()
        _alert_subscribers.append(alert_queue)
        
        def generate():
            try:
                while True:
                    try:
                        alert = alert_queue.get(timeout=30)
                        import json
                        yield f"data: {json.dumps(alert)}\n\n"
                    except:
                        yield ": keepalive\n\n"
            except GeneratorExit:
                if alert_queue in _alert_subscribers:
                    _alert_subscribers.remove(alert_queue)
        
        return app.response_class(
            generate(),
            mimetype='text/event-stream'
        )
    
    # ==================== ERROR HANDLERS ====================
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({'error': 'Internal server error'}), 500
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
