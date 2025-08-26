#!/usr/bin/env python3
# filepath: /home/gab/Geonovis-Api/assets/scripts/url_validator.py
import re
import sys
import urllib.parse
from collections import Counter

def check_url_characters(url_string):
    """
    Check a string for characters that would be problematic in a URL.
    Returns details about invalid and percent-encoded characters.
    """
    # Characters that must be percent-encoded in URLs
    reserved_chars = set(";/?:@&=+$,#")
    
    # Characters that are generally problematic in URLs
    problematic_chars = set("<>\"'%{}|\\^~[]`")
    
    # Control characters are always invalid
    control_chars = set(chr(i) for i in range(32)) | {chr(127)}
    
    # Results tracking
    invalid_chars = []
    reserved_found = []
    encoded_chars = []
    
    # Check each character
    for i, char in enumerate(url_string):
        if char in control_chars:
            invalid_chars.append((i, char, f"Control character (ASCII {ord(char)})"))
        elif char in problematic_chars:
            invalid_chars.append((i, char, "Problematic character"))
        elif char in reserved_chars:
            reserved_found.append((i, char))
        elif ord(char) > 127:  # Non-ASCII
            invalid_chars.append((i, char, f"Non-ASCII character (Unicode U+{ord(char):04X})"))
    
    # Check if percent encoding is needed
    encoded_url = urllib.parse.quote(url_string)
    if encoded_url != url_string:
        # Find all percent-encoded sequences
        for match in re.finditer('%[0-9A-Fa-f]{2}', encoded_url):
            orig_char = url_string[match.start() // 3]  # Approximate position
            encoded_chars.append((orig_char, match.group()))
    
    return {
        "invalid": invalid_chars,
        "reserved": reserved_found,
        "encoded_needed": encoded_chars,
        "original": url_string,
        "encoded": encoded_url,
        "char_counts": Counter(url_string)
    }

def print_report(results):
    """Print a formatted report of URL validation results."""
    print(f"URL Character Validation Report")
    print("-" * 50)
    
    # Original string info
    print(f"Original string length: {len(results['original'])} characters")
    if len(results['original']) > 100:
        preview = f"{results['original'][:50]}...{results['original'][-50:]}"
    else:
        preview = results['original']
    print(f"Preview: {preview}")
    print()
    
    # Invalid characters
    if results['invalid']:
        print(f"❌ Found {len(results['invalid'])} invalid characters:")
        for pos, char, reason in results['invalid']:
            print(f"  Position {pos}: '{char}' ({reason})")
        print()
    else:
        print("✅ No invalid characters found")
        print()
    
    # Reserved characters
    if results['reserved']:
        print(f"⚠️ Found {len(results['reserved'])} reserved characters:")
        for pos, char in results['reserved']:
            print(f"  Position {pos}: '{char}'")
        print()
    else:
        print("✅ No reserved characters found")
        print()
    
    # Encoding
    if results['encoded_needed']:
        print(f"🔄 Characters requiring percent-encoding:")
        for char, encoded in set(results['encoded_needed']):
            count = results['char_counts'][char]
            print(f"  '{char}' → {encoded} (occurs {count} times)")
        print()
        
        encoded_len = len(results['encoded'])
        original_len = len(results['original'])
        diff = encoded_len - original_len
        percent = (diff / original_len) * 100 if original_len > 0 else 0
        
        print(f"Encoded URL length: {encoded_len} characters")
        print(f"Encoding overhead: +{diff} characters ({percent:.1f}%)")
    else:
        print("✅ No encoding needed")
    
    print("-" * 50)

def main():
    """Main function to run the URL validator."""
    # Check if input is from a file or command line
    if len(sys.argv) > 1:
        # Check if it's a file
        filename = sys.argv[1]
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                url_string = f.read().strip()
            print(f"Reading from file: {filename}")
        except (FileNotFoundError, IsADirectoryError):
            # Not a file, treat as direct input
            url_string = sys.argv[1]
    else:
        # Prompt for input
        print("Enter URL string to validate:")
        url_string = input().strip()
    
    # Run the validation
    results = check_url_characters(url_string)
    print_report(results)

if __name__ == "__main__":
    main()