#!/usr/bin/env python3
# filepath: /home/gab/Geonovis-Api/src/server.py
from flask import Flask, jsonify, request, send_file, make_response
from flask_cors import CORS  # Add this import
import os
import sys
from pathlib import Path
import logging

# Add the src directory to the path so we can import our modules
sys.path.append(str(Path(__file__).parent))
from utils.geocode_service import get_merged_geocodes

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes
PORT = 3111

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.route('/')
def home():
    return 'Welcome to the Geonovis API!'

@app.route('/api/geojson/<region>')
def get_geojson(region):
    print(f"Requested region: {region}")
    file_path = Path(__file__).parent.parent / 'assets' / 'geojson' / region / f"{region}.geo.json"
    
    if not file_path.exists():
        logger.error(f"Error: File not found - {file_path}")
        return jsonify({
            'error': 'Region file not found',
            'details': f"Could not find {region}.geojson in assets/{region}/"
        }), 404
    
    try:
        response = send_file(file_path, mimetype='application/json')
        logger.info(f"Sent: {region}.geo.json")
        return response
    except Exception as e:
        logger.error(f"Error sending file: {str(e)}")
        return '', 500

@app.route('/api/geocodes')
def get_geocodes():
    print(f"Requested region: ")
    regions = request.args.get('regions')
    if not regions:
        return jsonify({
            'error': 'Missing regions parameter',
            'details': 'Please provide a regions parameter with a comma-separated list of region names'
        }), 400
    
    region_list = [region.strip() for region in regions.split(',')]
    geocodes_base_path = Path(__file__).parent.parent / 'assets' / 'geocodes'
    
    try:
        unique_geocodes = get_merged_geocodes(region_list, str(geocodes_base_path))
        logger.info(f"Provided geocodes for regions: {', '.join(region_list)}")
        return jsonify(unique_geocodes)
    except Exception as e:
        logger.error(f"Error processing geocodes: {str(e)}")
        return jsonify({
            'error': 'Failed to process geocodes',
            'details': str(e)
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=PORT, debug=True)
    print(f"Server is running on http://localhost:{PORT}")