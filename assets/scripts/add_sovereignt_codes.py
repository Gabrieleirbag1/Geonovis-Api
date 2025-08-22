#!/usr/bin/env python3
# filepath: process_geojson.py

import json
import os

def process_geojson(input_file, output_file):
    # Read the original GeoJSON file
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Define exceptions for countries with invalid codes
    exceptions = {
        "Serranilla Bank": "CO",        # Administered by Colombia
        "Scarborough Reef": "PH",       # Claimed by Philippines (disputed with China)
        "Southern Patagonian Ice Field": "AR",  # Shared between Argentina and Chile
        "Somaliland": "SO",             # Internationally recognized as part of Somalia
        "Bir Tawil": "EG",               # Unclaimed territory (using Egypt as nearest sovereign)
        "Palestine": "PS",               # Recognized by many countries, but not universally
    }
    
    # Process each feature to add code property based on iso_a2_eh
    for feature in data['features']:
        if 'properties' in feature and 'iso_a2_eh' in feature['properties']:
            country_name = feature['properties'].get('name')
            feature['properties']['code'] = feature['properties']['iso_a2_eh']

            # Check if the country is in our exceptions list
            if country_name in exceptions:
                feature['properties']['code'] = exceptions[country_name]
                print(f"Adding exception code: {exceptions[country_name]} for {country_name}")
                continue
                
            # Add the code property based on iso_a2_eh
            sovereignt = feature['properties']["sovereignt"]
            for country in data['features']:
                if country['properties']["name"] == sovereignt:
                    if country['properties']['iso_a2_eh'] == "-99" or country['properties']['iso_a2_eh'] == -99:
                        break
                    # print(f"Adding code: {country['properties']['iso_a2_eh']} for {feature['properties']['name']}")
                    feature['properties']['code'] = country['properties']['iso_a2_eh']
                    break

    print(data["features"][126]["properties"]["code"])
    # Write the updated GeoJSON to the output file
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False)
    
    print(f"Processing complete. Output saved to {output_file}")

if __name__ == "__main__":
    input_file = "src/assets/geo/custom3.geo.json"
    output_file = "src/assets/geo/custom3_with_codes.geo.json"
    
    # Ensure the input file exists
    if not os.path.exists(input_file):
        print(f"Error: Input file {input_file} not found.")
        exit(1)
    
    process_geojson(input_file, output_file)