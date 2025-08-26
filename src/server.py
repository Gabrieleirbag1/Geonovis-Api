#!/usr/bin/env python3
from flask import Flask, jsonify, request, send_file, Response
from flask_cors import CORS  # Add this import
import sys
from pathlib import Path
from lite_logging.lite_logging import log

# Add the src directory to the path so we can import our modules
sys.path.append(str(Path(__file__).parent))
from utils.geocode_service import get_merged_geocodes

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes
PORT = 3111

@app.route('/')
def home():
    return 'Welcome to the Geonovis API!'

@app.route('/api/geojson/<region>')
def get_geojson(region: str) -> Response:
    file_path: Path = Path(__file__).parent.parent / 'assets' / 'geojson' / region / f"{region}.geo.json"

    if not file_path.exists():
        log("File not found", level="ERROR")
        return jsonify({
            'error': 'Region file not found',
            'details': f"Could not find {region}.geojson in assets/{region}/"
        }), 404
    
    try:
        response: Response = send_file(file_path, mimetype='application/json')
        log(f"Served geojson for region: {region}", level="INFO")
        return response
    except Exception as e:
        log(f"Error sending file: {str(e)}", level="ERROR")
        return '', 500

@app.route('/api/geocodes')
def get_geocodes() -> Response:
    regions: list[str] = request.args.get('regions')
    if not regions:
        return jsonify({
            'error': 'Missing regions parameter',
            'details': 'Please provide a regions parameter with a comma-separated list of region names'
        }), 400
    
    region_list = [region.strip() for region in regions.split(',')]
    geocodes_base_path = Path(__file__).parent.parent / 'assets' / 'geocodes'
    
    try:
        unique_geocodes = get_merged_geocodes(region_list, str(geocodes_base_path))
        log(f"Served geocodes for regions: {region_list}", level="INFO")
        return jsonify(unique_geocodes)
    except Exception as e:
        log(f"Error processing geocodes: {str(e)}", level="ERROR")
        return jsonify({
            'error': 'Failed to process geocodes',
            'details': str(e)
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=PORT, debug=True)
    print(f"Server is running on http://localhost:{PORT}")