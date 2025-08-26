#!/usr/bin/env python3
# filepath: /home/gab/Geonovis-Api/assets/scripts/b32/base32_to_json.py
import json
import base64
import os
import sys

def base32_to_json(input_file):
    try:
        # Read the base32 file
        with open(input_file, 'r', encoding='utf-8') as f:
            encoded = f.read().strip()
        
        # Decode base32 to JSON
        json_bytes = base64.b32decode(encoded)
        json_str = json_bytes.decode('utf-8')
        data = json.loads(json_str)
        
        # Create output filename
        output_file = os.path.splitext(input_file)[0] + '.json'
        
        # Write to output file
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        
        print(f"Converted Base32 to JSON and saved to {output_file}")
        
    except FileNotFoundError:
        print(f"Error: File '{input_file}' not found.")
        sys.exit(1)
    except base64.binascii.Error:
        print(f"Error: File '{input_file}' does not contain valid Base32 data.")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Error: The decoded content is not valid JSON.")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
    else:
        input_file = os.path.join(os.path.dirname(__file__), "test.b32")
        if not os.path.exists(input_file):
            print("Error: No input file specified and test.b32 not found.")
            print("Usage: python base32_to_json.py <input_file.b32>")
            sys.exit(1)
    
    base32_to_json(input_file)