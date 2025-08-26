#!/usr/bin/env python3
# filepath: /home/gab/Geonovis-Api/assets/scripts/conversion/json_to_mp_br_b85_b64url.py

import json
import base64
import os
import sys
import argparse
import re

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

def base64_to_base64url(b64str):
    """Convert standard base64 to URL-safe base64."""
    return b64str.replace('+', '-').replace('/', '_').rstrip('=')

def encode_json_file(input_file, output_file=None, quality=11):
    """
    Encode a JSON file using MessagePack, Brotli, Base85, and Base64URL.
    
    Pipeline: JSON → MessagePack → Brotli → Base85 → Base64URL
    
    Args:
        input_file (str): Path to the JSON file to encode
        output_file (str, optional): Path to save the encoded file
        quality (int, optional): Brotli compression quality (0-11)
    
    Returns:
        tuple: (success, stats_dict, output_path)
    """
    try:
        # Determine output file path if not specified
        if not output_file:
            output_file = os.path.splitext(input_file)[0] + '.mpbrb85b64url'
        
        # Read and parse JSON
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Step 1: Convert to MessagePack
        msgpacked = msgpack.packb(data, use_bin_type=True)
        
        # Step 2: Compress with Brotli
        compressed = brotli.compress(msgpacked, quality=quality)
        
        # Step 3: Encode with Base85
        b85_encoded = base64.a85encode(compressed).decode('utf-8')
        
        # Step 4: Convert to Base64URL-safe format
        # First, convert back to binary to get proper base64
        binary = base64.a85decode(b85_encoded)
        b64_encoded = base64.b64encode(binary).decode('utf-8')
        b64url_encoded = base64_to_base64url(b64_encoded)
        
        # Write to output file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(b64url_encoded)
        
        # Calculate compression stats
        json_str = json.dumps(data, separators=(',', ':'))
        original_json_size = len(json_str.encode('utf-8'))
        msgpack_size = len(msgpacked)
        compressed_size = len(compressed)
        b85_size = len(b85_encoded)
        final_size = len(b64url_encoded)
        
        stats = {
            'original_json_size': original_json_size,
            'msgpack_size': msgpack_size,
            'compressed_size': compressed_size,
            'base85_size': b85_size,
            'final_size': final_size,
            'msgpack_ratio': original_json_size / msgpack_size,
            'compression_ratio': msgpack_size / compressed_size,
            'encoding_ratio': compressed_size / final_size,
            'total_ratio': original_json_size / final_size
        }
        
        return (True, stats, output_file)
        
    except FileNotFoundError:
        return (False, f"Input file not found: {input_file}", None)
    except json.JSONDecodeError:
        return (False, f"Invalid JSON in file: {input_file}", None)
    except Exception as e:
        return (False, f"Error: {str(e)}", None)

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description='Encode JSON using MessagePack, Brotli, Base85, and Base64URL')
    parser.add_argument('input', help='Input JSON file')
    parser.add_argument('-o', '--output', help='Output file (default: input file with .mpbrb85b64url extension)')
    parser.add_argument('-q', '--quality', type=int, choices=range(0, 12), default=11,
                        help='Brotli compression quality (0-11, default: 11)')
    
    args = parser.parse_args()
    
    # Process the file
    success, result, output_path = encode_json_file(args.input, args.output, args.quality)
    
    if success:
        print(f"Successfully encoded JSON to MessagePack+Brotli+Base85+Base64URL")
        print(f"Original JSON size: {result['original_json_size']} bytes")
        print(f"MessagePack size: {result['msgpack_size']} bytes (ratio: {result['msgpack_ratio']:.2f}x)")
        print(f"Compressed size: {result['compressed_size']} bytes (ratio: {result['compression_ratio']:.2f}x)")
        print(f"Base85 size: {result['base85_size']} characters")
        print(f"Final URL-safe size: {result['final_size']} characters")
        print(f"Overall compression: {result['total_ratio']:.2f}x")
        print(f"Output saved to: {output_path}")
        
        # Show URL safety info
        contains_url_unsafe = re.search(r'[^A-Za-z0-9\-_]', open(output_path, 'r').read())
        if contains_url_unsafe:
            print("\nWarning: Output contains characters that may need URL encoding in some contexts.")
        else:
            print("\n✓ Output is URL-safe (contains only alphanumeric, '-', and '_' characters)")
    else:
        print(f"Failed to encode: {result}")
        sys.exit(1)

if __name__ == "__main__":
    main()