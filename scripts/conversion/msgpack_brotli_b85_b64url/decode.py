#!/usr/bin/env python3
# filepath: /home/gab/Geonovis-Api/assets/scripts/conversion/mp_br_b85_b64url_to_json.py

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

try:
    import msgpack
except ImportError:
    print("Error: MessagePack library not installed.")
    print("Please install it with: pip install msgpack")
    sys.exit(1)

def base64url_to_base64(b64url):
    """Convert URL-safe base64 to standard base64."""
    # Replace URL-safe characters
    b64 = b64url.replace('-', '+').replace('_', '/')
    # Add padding if needed
    padding = len(b64) % 4
    if padding:
        b64 += '=' * (4 - padding)
    return b64

def decode_file(input_file, output_file=None, pretty=False):
    """
    Decode a MessagePack+Brotli+Base85+Base64URL encoded file back to JSON.
    
    Pipeline: Base64URL → Base85 → Brotli → MessagePack → JSON
    
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
        
        # Step 1: Convert from Base64URL to Base64
        b64_str = base64url_to_base64(encoded)
        
        # Step 2: Decode Base64 to binary
        try:
            binary = base64.b64decode(b64_str)
        except Exception as e:
            return (False, f"Invalid Base64 encoding: {e}", None)
        
        # Step 3: Decode Base85 (we re-encode to Base85 and then decode)
        try:
            b85_encoded = base64.a85encode(binary).decode('utf-8')
            decompressed = base64.a85decode(b85_encoded)
        except Exception as e:
            return (False, f"Invalid Base85 encoding: {e}", None)
        
        # Step 4: Decompress with Brotli
        try:
            msgpacked = brotli.decompress(decompressed)
        except Exception as e:
            return (False, f"Invalid Brotli compressed data: {e}", None)
        
        # Step 5: Unpack MessagePack
        try:
            data = msgpack.unpackb(msgpacked, raw=False)
        except Exception as e:
            return (False, f"Invalid MessagePack data: {e}", None)
        
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
    parser = argparse.ArgumentParser(
        description='Decode MessagePack+Brotli+Base85+Base64URL encoded files to JSON')
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