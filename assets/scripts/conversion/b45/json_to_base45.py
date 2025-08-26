import zlib, base45, json, os, sys

# Load data from a JSON file
if len(sys.argv) > 1:
    input_file = sys.argv[1]
else:
    input_file = os.path.join(os.path.dirname(__file__), "test.json")

try:
    with open(input_file, "r", encoding="utf-8") as f:
        data = json.load(f)
except FileNotFoundError:
    print(f"Error: File '{input_file}' not found.")
    sys.exit(1)
except json.JSONDecodeError:
    print(f"Error: File '{input_file}' is not valid JSON.")
    sys.exit(1)

# Process the data
print("Original data:", data)
json_str = json.dumps(data, separators=(',', ':'))  # minify
compressed = zlib.compress(json_str.encode("utf-8"))
encoded = base45.b45encode(compressed).decode("utf-8")

print("JSON size:", len(json_str), "bytes")
print("QR code size:", len(encoded), "bytes")
print("Base45:", encoded)

# Optionally save the encoded data
output_file = os.path.splitext(input_file)[0] + ".b45"
with open(output_file, "w", encoding="utf-8") as f:
    f.write(encoded)
print(f"Encoded data saved to {output_file}")