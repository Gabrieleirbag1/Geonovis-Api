#!/usr/bin/env python3
# filepath: /home/gab/Geonovis-Api/assets/scripts/conversion/json_to_brotli_b64.py

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

def encode_json_file(input_file, output_file=None, quality=11):
    """
    Encode a JSON file using Brotli compression and Base64 encoding.
    
    Args:
        input_file (str): Path to the JSON file to encode
        output_file (str, optional): Path to save the encoded file (defaults to input_file + .brb64)
        quality (int, optional): Brotli compression quality (0-11, higher is better compression)
    
    Returns:
        tuple: (success, message, output_path)
    """
    try:
        # Determine output file path if not specified
        if not output_file:
            output_file = os.path.splitext(input_file)[0] + '.brb64'
        
        # Read and parse JSON
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Convert to compact JSON string
        json_str = json.dumps(data, separators=(',', ':'))
        json_bytes = json_str.encode('utf-8')
        
        # Compress with Brotli
        compressed = brotli.compress(json_bytes, quality=quality)
        
        # Encode with Base64
        encoded = base64.b64encode(compressed).decode('utf-8')
        
        # Write to output file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(encoded)
        
        # Calculate compression stats
        original_size = len(json_bytes)
        compressed_size = len(compressed)
        encoded_size = len(encoded)
        
        compression_ratio = original_size / compressed_size
        encoding_overhead = encoded_size / compressed_size
        total_ratio = original_size / encoded_size
        
        return (True, {
            'original_size': original_size,
            'compressed_size': compressed_size,
            'encoded_size': encoded_size,
            'compression_ratio': compression_ratio,
            'encoding_overhead': encoding_overhead,
            'total_ratio': total_ratio
        }, output_file)
        
    except FileNotFoundError:
        return (False, f"Input file not found: {input_file}", None)
    except json.JSONDecodeError:
        return (False, f"Invalid JSON in file: {input_file}", None)
    except Exception as e:
        return (False, f"Error: {str(e)}", None)

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Encode JSON using Brotli compression and Base64 encoding')
    parser.add_argument('input', help='Input JSON file')
    parser.add_argument('-o', '--output', help='Output file (default: input file with .brb64 extension)')
    parser.add_argument('-q', '--quality', type=int, choices=range(0, 12), default=11,
                        help='Brotli compression quality (0-11, default: 11)')
    
    args = parser.parse_args()
    
    # Process the file
    success, result, output_path = encode_json_file(args.input, args.output, args.quality)
    
    if success:
        print(f"Successfully encoded JSON to Brotli+Base64")
        print(f"Original JSON size: {result['original_size']} bytes")
        print(f"Compressed size: {result['compressed_size']} bytes (ratio: {result['compression_ratio']:.2f}x)")
        print(f"Final encoded size: {result['encoded_size']} bytes (overhead: {result['encoding_overhead']:.2f}x)")
        print(f"Overall compression: {result['total_ratio']:.2f}x")
        print(f"Output saved to: {output_path}")
    else:
        print(f"Failed to encode: {result}")
        sys.exit(1)

if __name__ == "__main__":
    main()