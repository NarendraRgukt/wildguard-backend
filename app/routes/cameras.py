from flask import Blueprint

cameras_bp = Blueprint('cameras', __name__, url_prefix='/api/cameras')

# Camera event ingestion and processing routes will be added here
