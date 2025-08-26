#!/usr/bin/env python3
# filepath: /home/gab/Geonovis-Api/assets/scripts/qr_optimize/decode_optimized.py
import json
import zlib
import base64
import base45
import os
import sys
import msgpack

try:
    import brotli
    HAVE_BROTLI = True
except ImportError:
    HAVE_BROTLI = False
    print("Warning: Brotli not installed. Some files may not decode properly.")

def decode_file(input_file):
    try:
        # Read the encoded file
        with open(input_file, 'r', encoding='utf-8') as f:
            encoded = f.read().strip()
        
        file_ext = os.path.splitext(input_file)[1].lower()
        
        # Determine the decoding method based on file extension
        if file_ext == '.zlb45':
            # zlib + Base45
            compressed = base45.b45decode(encoded)
            decompressed = zlib.decompress(compressed)
            data = json.loads(decompressed.decode('utf-8'))
        elif file_ext == '.zlb64':
            # zlib + Base64
            compressed = base64.b64decode(encoded)
            decompressed = zlib.decompress(compressed)
            data = json.loads(decompressed.decode('utf-8'))
        elif file_ext == '.zla85':
            # zlib + Base85
            compressed = base64.a85decode(encoded)
            decompressed = zlib.decompress(compressed)
            data = json.loads(decompressed.decode('utf-8'))
        elif file_ext == '.brb64' and HAVE_BROTLI:
            # Brotli + Base64
            compressed = base64.b64decode(encoded)
            decompressed = brotli.decompress(compressed)
            data = json.loads(decompressed.decode('utf-8'))
        elif file_ext == '.bra85' and HAVE_BROTLI:
            # Brotli + Base85
            compressed = base64.a85decode(encoded)
            decompressed = brotli.decompress(compressed)
            data = json.loads(decompressed.decode('utf-8'))
        elif file_ext == '.msgzlb64':
            # MessagePack + zlib + Base64
            compressed = base64.b64decode(encoded)
            decompressed = zlib.decompress(compressed)
            data = msgpack.unpackb(decompressed, raw=False)
        elif file_ext == '.msgzla85':
            # MessagePack + zlib + Base85
            compressed = base64.a85decode(encoded)
            decompressed = zlib.decompress(compressed)
            data = msgpack.unpackb(decompressed, raw=False)
        elif file_ext == '.msgbra85' and HAVE_BROTLI:
            # MessagePack + Brotli + Base85
            compressed = base64.a85decode(encoded)
            decompressed = brotli.decompress(compressed)
            data = msgpack.unpackb(decompressed, raw=False)
        else:
            print(f"Unsupported file extension: {file_ext}")
            return
        
        # Save as JSON
        output_file = os.path.splitext(input_file)[0] + '.decoded.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        
        print(f"Successfully decoded to {output_file}")
        
    except Exception as e:
        print(f"Error decoding: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
    else:
        print("Please specify an input file")
        print("Usage: python decode_optimized.py <encoded-file>")
        sys.exit(1)
    
    decode_file(input_file)