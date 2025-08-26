#!/usr/bin/env python3
# filepath: /home/gab/Geonovis-Api/assets/scripts/qr_optimize/optimize_for_qr.py
import json
import zlib
import base64
import base45
import os
import sys
import msgpack

# Try to import optional dependencies
try:
    import brotli
    HAVE_BROTLI = True
except ImportError:
    HAVE_BROTLI = False
    print("Brotli not installed. For better compression: pip install brotli")

try:
    import base85
    HAVE_BASE85 = True
except ImportError:
    HAVE_BASE85 = False
    # We'll fall back to Python's built-in base85 (ascii85)

def compare_encodings(input_file):
    try:
        # Read the JSON file
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Convert JSON to string (minified)
        json_str = json.dumps(data, separators=(',', ':'))
        
        # Convert to MessagePack (more compact binary serialization)
        msgpacked = msgpack.packb(data, use_bin_type=True)
        
        results = []
        
        # Original JSON size
        results.append(("Original JSON", len(json_str), None, None))
        
        # MessagePack binary
        results.append(("MessagePack binary", len(msgpacked), None, None))
        
        # 1. Simple Base64 (no compression)
        encoded = base64.b64encode(json_str.encode('utf-8')).decode('utf-8')
        results.append(("JSON + Base64", len(encoded), encoded[:50] + "...", None))
        
        # 2. MessagePack + Base64
        encoded = base64.b64encode(msgpacked).decode('utf-8')
        results.append(("MessagePack + Base64", len(encoded), encoded[:50] + "...", None))
        
        # 3. zlib + Base64
        compressed = zlib.compress(json_str.encode('utf-8'), level=9)
        encoded = base64.b64encode(compressed).decode('utf-8')
        results.append(("JSON + zlib + Base64", len(encoded), encoded[:50] + "...", 
                         os.path.splitext(input_file)[0] + ".zlb64"))
        
        # 4. zlib + MessagePack + Base64
        compressed = zlib.compress(msgpacked, level=9)
        encoded = base64.b64encode(compressed).decode('utf-8')
        results.append(("MessagePack + zlib + Base64", len(encoded), encoded[:50] + "...",
                         os.path.splitext(input_file)[0] + ".msgzlb64"))
        
        # 5. zlib + Base45 (your current method)
        compressed = zlib.compress(json_str.encode('utf-8'))
        encoded = base45.b45encode(compressed).decode('utf-8')
        results.append(("JSON + zlib + Base45", len(encoded), encoded[:50] + "...", 
                         os.path.splitext(input_file)[0] + ".zlb45"))
        
        # 6. Built-in base85 (ascii85)
        compressed = zlib.compress(json_str.encode('utf-8'), level=9)
        encoded = base64.a85encode(compressed).decode('utf-8')
        results.append(("JSON + zlib + Base85", len(encoded), encoded[:50] + "...",
                         os.path.splitext(input_file)[0] + ".zla85"))
        
        # 7. MessagePack + zlib + Base85
        compressed = zlib.compress(msgpacked, level=9)
        encoded = base64.a85encode(compressed).decode('utf-8')
        results.append(("MessagePack + zlib + Base85", len(encoded), encoded[:50] + "...",
                         os.path.splitext(input_file)[0] + ".msgzla85"))
        
        # 8. Brotli compression if available (usually better than zlib)
        if HAVE_BROTLI:
            compressed = brotli.compress(json_str.encode('utf-8'), quality=11)
            encoded = base64.b64encode(compressed).decode('utf-8')
            results.append(("JSON + Brotli + Base64", len(encoded), encoded[:50] + "...",
                             os.path.splitext(input_file)[0] + ".brb64"))
            
            # Brotli + Base85 (likely the best combination)
            encoded = base64.a85encode(compressed).decode('utf-8')
            results.append(("JSON + Brotli + Base85", len(encoded), encoded[:50] + "...",
                             os.path.splitext(input_file)[0] + ".bra85"))
            
            # MessagePack + Brotli + Base85 (could be the very best)
            compressed = brotli.compress(msgpacked, quality=11)
            encoded = base64.a85encode(compressed).decode('utf-8')
            results.append(("MessagePack + Brotli + Base85", len(encoded), encoded[:50] + "...",
                             os.path.splitext(input_file)[0] + ".msgbra85"))
        
        # Sort by size
        results.sort(key=lambda x: x[1])
        
        # Print results
        print(f"\nCompression comparison for {input_file}:")
        print("-" * 80)
        print(f"{'Method':<30} {'Size (chars)':<15} {'Sample':<35}")
        print("-" * 80)
        
        for method, size, sample, output_file in results:
            print(f"{method:<30} {size:<15} {sample if sample else 'N/A'}")
        
        # Save the best text encoding
        best_method = next((r for r in results if r[3] and r[1] == min(r[1] for r in results if r[3])), None)
        if best_method:
            method, size, sample, output_file = best_method
            
            # Get the encoded data again (we only stored a sample before)
            if "Brotli" in method and HAVE_BROTLI:
                if "MessagePack" in method:
                    compressed = brotli.compress(msgpacked, quality=11)
                else:
                    compressed = brotli.compress(json_str.encode('utf-8'), quality=11)
                
                if "Base85" in method:
                    encoded = base64.a85encode(compressed).decode('utf-8')
                else:
                    encoded = base64.b64encode(compressed).decode('utf-8')
            elif "zlib" in method:
                if "MessagePack" in method:
                    compressed = zlib.compress(msgpacked, level=9)
                else:
                    compressed = zlib.compress(json_str.encode('utf-8'), level=9)
                
                if "Base85" in method:
                    encoded = base64.a85encode(compressed).decode('utf-8')
                elif "Base45" in method:
                    encoded = base45.b45encode(compressed).decode('utf-8')
                else:
                    encoded = base64.b64encode(compressed).decode('utf-8')
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(encoded)
            print(f"\nBest method: {method}")
            print(f"Saved to: {output_file}")
            print(f"Size: {size} characters")
            
            # Calculate QR code complexity estimate
            qr_version = 1
            capacity = 17
            while capacity < size and qr_version < 40:
                qr_version += 1
                capacity = (qr_version * 4 + 17) ** 2 // 8 * 0.8  # Rough estimate
            
            if qr_version <= 40:
                print(f"Estimated QR code version: {qr_version} (of 40)")
            else:
                print("Warning: Data may be too large for a single QR code")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
    else:
        input_file = os.path.join(os.path.dirname(__file__), "test.json")
    
    compare_encodings(input_file)