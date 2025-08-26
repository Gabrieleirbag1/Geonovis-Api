#!/usr/bin/env python3
# filepath: /home/gab/Geonovis-Api/assets/scripts/conversion/brotli_b64_to_json.py

import json
import base64
import os
import sys
import argparse

try:
    import brotli
except ImportError:
    print("Error: Brotli compression library not installed.")
    print("Please install it with: pip install brotli")
    sys.exit(1)

def decode_file(input_file, output_file=None, pretty=False):
    """
    Decode a Brotli+Base64 encoded file back to JSON.
    
    Args:
        input_file (str): Path to the encoded file
        output_file (str, optional): Path to save the decoded JSON file
        pretty (bool): Whether to format the JSON with indentation
    
    Returns:
        tuple: (success, message, output_path)
    """
    try:
        # Determine output file path if not specified
        if not output_file:
            output_file = os.path.splitext(input_file)[0] + '.json'
        
        # Read the encoded content
        with open(input_file, 'r', encoding='utf-8') as f:
            encoded = f.read().strip()
        
        # Decode Base64
        try:
            compressed = base64.b64decode(encoded)
        except Exception:
            return (False, "Invalid Base64 encoding", None)
        
        # Decompress with Brotli
        try:
            json_bytes = brotli.decompress(compressed)
        except Exception:
            return (False, "Invalid Brotli compressed data", None)
        
        # Parse JSON
        try:
            json_str = json_bytes.decode('utf-8')
            data = json.loads(json_str)
        except UnicodeDecodeError:
            return (False, "Decompressed data is not valid UTF-8", None)
        except json.JSONDecodeError:
            return (False, "Decompressed data is not valid JSON", None)
        
        # Write the decoded JSON
        with open(output_file, 'w', encoding='utf-8') as f:
            if pretty:
                json.dump(data, f, indent=2)
            else:
                json.dump(data, f, separators=(',', ':'))
        
        return (True, "Decoded successfully", output_file)
    
    except FileNotFoundError:
        return (False, f"Input file not found: {input_file}", None)
    except Exception as e:
        return (False, f"Error: {str(e)}", None)

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Decode Brotli+Base64 encoded JSON files')
    parser.add_argument('input', help='Input encoded file')
    parser.add_argument('-o', '--output', help='Output JSON file (default: input file with .json extension)')
    parser.add_argument('-p', '--pretty', action='store_true', help='Format JSON with indentation')
    
    args = parser.parse_args()
    
    # Process the file
    success, message, output_path = decode_file(args.input, args.output, args.pretty)
    
    if success:
        print(f"Successfully decoded to JSON")
        print(f"Output saved to: {output_path}")
    else:
        print(f"Failed to decode: {message}")
        sys.exit(1)

if __name__ == "__main__":
    main()