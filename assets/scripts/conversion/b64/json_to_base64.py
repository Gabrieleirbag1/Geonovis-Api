#!/usr/bin/env python3
# filepath: /home/gab/Geonovis-Api/assets/scripts/json_to_base64.py
import json
import base64
import os
import sys

def json_to_base64(input_file):
    try:
        # Read the JSON file
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Convert JSON to string and encode to base64
        json_str = json.dumps(data, separators=(',', ':'))  # Minify JSON
        encoded = base64.b64encode(json_str.encode('utf-8')).decode('utf-8')
        
        # Create output filename
        output_file = os.path.splitext(input_file)[0] + '.b64'
        
        # Write to output file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(encoded)
        
        print(f"JSON size: {len(json_str)} bytes")
        print(f"Base64 size: {len(encoded)} bytes")
        print(f"Converted JSON to Base64 and saved to {output_file}")
        
    except FileNotFoundError:
        print(f"Error: File '{input_file}' not found.")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Error: File '{input_file}' is not valid JSON.")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
    else:
        input_file = os.path.join(os.path.dirname(__file__), "test.json")
        if not os.path.exists(input_file):
            print("Error: No input file specified and test.json not found.")
            print("Usage: python json_to_base64.py <input_file.json>")
            sys.exit(1)
    
    json_to_base64(input_file)