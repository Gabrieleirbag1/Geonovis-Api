#!/usr/bin/env python3
# filepath: /home/gab/Geonovis-Api/src/utils/session_codec.py

import json
import base64
import sys
import re
from typing import Dict, Any, Tuple, Union

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


class SessionCodec:
    """
    Utility class for encoding and decoding session data using
    MessagePack + Brotli + Base85 + Base64URL.
    """
    
    @staticmethod
    def base64_to_base64url(b64str: str) -> str:
        """Convert standard base64 to URL-safe base64."""
        return b64str.replace('+', '-').replace('/', '_').rstrip('=')
    
    @staticmethod
    def base64url_to_base64(b64url: str) -> str:
        """Convert URL-safe base64 to standard base64."""
        # Replace URL-safe characters
        b64 = b64url.replace('-', '+').replace('_', '/')
        # Add padding if needed
        padding = len(b64) % 4
        if padding:
            b64 += '=' * (4 - padding)
        return b64
    
    @classmethod
    def encode(cls, data: Dict[str, Any], quality: int = 11) -> Dict[str, Union[bool, str, Dict]]:
        """
        Encode JSON data using MessagePack, Brotli, Base85, and Base64URL.
        
        Pipeline: JSON → MessagePack → Brotli → Base85 → Base64URL
        
        Args:
            data: The JSON data to encode
            quality: Brotli compression quality (0-11)
            
        Returns:
            Dictionary with success status, encoded content, and stats
        """
        try:
            # Convert to compact JSON string for size comparison
            json_str = json.dumps(data, separators=(',', ':'))
            original_json_size = len(json_str.encode('utf-8'))
            
            # Step 1: Convert to MessagePack
            msgpacked = msgpack.packb(data, use_bin_type=True)
            msgpack_size = len(msgpacked)
            
            # Step 2: Compress with Brotli
            compressed = brotli.compress(msgpacked, quality=quality)
            compressed_size = len(compressed)
            
            # Step 3: Encode with Base85
            b85_encoded = base64.a85encode(compressed).decode('utf-8')
            b85_size = len(b85_encoded)
            
            # Step 4: Convert to Base64URL-safe format
            binary = base64.a85decode(b85_encoded)
            b64_encoded = base64.b64encode(binary).decode('utf-8')
            b64url_encoded = cls.base64_to_base64url(b64_encoded)
            final_size = len(b64url_encoded)
            
            # Calculate compression stats
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
            
            # Check URL safety
            contains_url_unsafe = bool(re.search(r'[^A-Za-z0-9\-_]', b64url_encoded))
            if contains_url_unsafe:
                stats['warning'] = 'Output contains characters that may need URL encoding in some contexts'
            
            return {
                "success": True,
                "content": b64url_encoded,
                "stats": stats
            }
            
        except Exception as e:
            return {
                "success": False,
                "content": None,
                "error": str(e)
            }
    
    @classmethod
    def decode(cls, encoded_data: str) -> Dict[str, Union[bool, Any, str]]:
        """
        Decode MessagePack+Brotli+Base85+Base64URL encoded data back to JSON.
        
        Pipeline: Base64URL → Base85 → Brotli → MessagePack → JSON
        
        Args:
            encoded_data: The encoded string
            
        Returns:
            Dictionary with success status and decoded content or error
        """
        try:
            # Step 1: Convert from Base64URL to Base64
            b64_str = cls.base64url_to_base64(encoded_data)
            
            # Step 2: Decode Base64 to binary
            try:
                binary = base64.b64decode(b64_str)
            except Exception as e:
                return {"success": False, "content": None, "error": f"Invalid Base64 encoding: {e}"}
            
            # Step 3: Decode Base85 (we re-encode to Base85 and then decode)
            try:
                b85_encoded = base64.a85encode(binary).decode('utf-8')
                decompressed = base64.a85decode(b85_encoded)
            except Exception as e:
                return {"success": False, "content": None, "error": f"Invalid Base85 encoding: {e}"}
            
            # Step 4: Decompress with Brotli
            try:
                msgpacked = brotli.decompress(decompressed)
            except Exception as e:
                return {"success": False, "content": None, "error": f"Invalid Brotli compressed data: {e}"}
            
            # Step 5: Unpack MessagePack
            try:
                data = msgpack.unpackb(msgpacked, raw=False)
            except Exception as e:
                return {"success": False, "content": None, "error": f"Invalid MessagePack data: {e}"}
            
            return {
                "success": True,
                "content": data
            }
        
        except Exception as e:
            return {
                "success": False,
                "content": None,
                "error": f"Decoding error: {str(e)}"
            }


# Example usage:
if __name__ == "__main__":
    # Test encoding
    test_data = {"name": "Example", "data": [1, 2, 3], "nested": {"a": True, "b": "test"}}
    
    encoded_result = SessionCodec.encode(test_data)
    print("Encoded:", encoded_result)
    
    # Test decoding
    if encoded_result["success"]:
        decoded_result = SessionCodec.decode(encoded_result["content"])
        print("Decoded:", decoded_result)