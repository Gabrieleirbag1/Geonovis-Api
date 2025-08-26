import zlib, base45, json, os, sys

# Load data from a base45 file
if len(sys.argv) > 1:
    input_file = sys.argv[1]
else:
    input_file = os.path.join(os.path.dirname(__file__), "test.b45")

try:
    with open(input_file, "r", encoding="utf-8") as f:
        encoded = f.read().strip()
except FileNotFoundError:
    print(f"Error: File '{input_file}' not found.")
    sys.exit(1)

try:
    # Decode base45 to JSON
    compressed = base45.b45decode(encoded)
    json_str = zlib.decompress(compressed).decode("utf-8")
    data = json.loads(json_str)
    
    # Print the decoded data
    print("Decoded data:", data)
    
    # Save the decoded data to a JSON file
    output_file = os.path.splitext(input_file)[0] + ".decoded.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    print(f"Decoded data saved to {output_file}")
    
except Exception as e:
    print(f"Error decoding data: {e}")
    sys.exit(1)