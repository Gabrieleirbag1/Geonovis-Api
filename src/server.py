#!/usr/bin/env python3
from flask import Flask, jsonify, request, send_file, Response
from flask_cors import CORS  # Add this import
import sys
from pathlib import Path
from lite_logging.lite_logging import log

# Add the src directory to the path so we can import our modules
sys.path.append(str(Path(__file__).parent))
from utils.geocode_service import get_merged_geocodes
from utils.session_codec import SessionCodec

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes
PORT = 3111

@app.route('/')
def home() -> Response:
    """Home route."""
    return 'Welcome to the Geonovis API!'

@app.route('/api/geojson/<region>')
def get_geojson(region: str) -> Response:
    """
    Get GeoJSON data for a specific region.

    Returns:
        Response: GeoJSON response for the specified region or error message.
    """
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
    """Get merged geocodes for specified regions.

    Returns:
        Response: JSON response containing merged geocodes or error message.
    """
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

@app.route('/api/session/encode', methods=['POST'])
def encode_session() -> Response:
    """
    Convert session data using MessagePack + Brotli + Base85 + Base64URL encoding.
    
    Returns:
        Response: JSON response containing encoded data or error message.
    """
    data = request.json
    log(f"Received session data for encoding: {data}", level="DEBUG")
    
    if not data:
        return jsonify({
            'success': False,
            'error': 'No data provided'
        }), 400
    
    result = SessionCodec.encode(data)
    
    if result["success"]:
        log(f"Successfully encoded session data", level="INFO")
        return jsonify(result)
    else:
        log(f"Failed to encode session data: {result['error']}", level="ERROR")
        return jsonify(result), 400

@app.route('/api/session/decode', methods=['POST'])
def decode_session() -> Response:
    """
    Decode session data from MessagePack + Brotli + Base85 + Base64URL format.
    
    Returns:
        Response: JSON response containing decoded data or error message.
    """
    data = request.json
    log(f"Received session data for decoding: {data}", level="DEBUG")
    
    if not data:
        return jsonify({
            'success': False,
            'error': 'No encoded content provided'
        }), 400

    result = SessionCodec.decode(data["sessionData"])

    if result["success"]:
        log(f"Successfully decoded session data", level="INFO")
        return jsonify(result)
    else:
        log(f"Failed to decode session data: {result['error']}", level="ERROR")
        return jsonify(result), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=PORT, debug=True)
    print(f"Server is running on http://localhost:{PORT}")