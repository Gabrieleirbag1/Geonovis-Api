#!/usr/bin/env python3
# filepath: /home/gab/GeoNovis/src/assets/geo/add_missing_countries.py

import json
import os
import glob

def load_geojson_countries():
    """Load country data from GeoJSON file"""
    with open('countries_with_codes.geo.json', 'r', encoding='utf-8') as f:
        geojson = json.load(f)
    return geojson

def load_world_infos():
    """Load country data from world-infos.json"""
    with open('../data/world-infos.json', 'r', encoding='utf-8') as f:
        world_infos = json.load(f)
    
    # Create a dictionary with country codes as keys and country names as values
    world_countries = {}
    for country in world_infos:
        if 'flag' in country and 'country' in country and 'fr' in country['country']:
            world_countries[country['flag'].lower()] = country['country']['fr']
    
    return world_countries

def add_missing_countries():
    """Add missing countries to GeoJSON file"""
    # Load the base GeoJSON file
    geojson = load_geojson_countries()
    world_countries = load_world_infos()
    
    # Get a list of all GeoJSON files in the 'other' directory
    other_files = glob.glob('other/*.geojson')
    
    # Process each file
    for file_path in other_files:
        country_name = os.path.basename(file_path).replace('.geojson', '')
        print(f"Processing {country_name}...")
        
        # Load the individual country GeoJSON
        with open(file_path, 'r', encoding='utf-8') as f:
            country_geojson = json.load(f)
        
        # Find the country code from world-infos.json
        country_code = None
        for code, name in world_countries.items():
            if name.lower() == country_name.lower():
                country_code = code
                break
            # Special case handling
            elif country_name.lower() == "hong kong" and name.lower() == "hong kong":
                country_code = "hk"
                break
            elif country_name.lower() == "puerto rico" and name.lower() == "porto rico":
                country_code = "pr"
                break
            elif country_name.lower() == "mauritius" and name.lower() == "maurice":
                country_code = "mu"
                break
            elif country_name.lower() == "seychelles" and name.lower() == "seychelles":
                country_code = "sc"
                break
            elif country_name.lower() == "tokelau":
                country_code = "tk"
                break
            elif country_name.lower() == "maldives" and name.lower() == "maldives":
                country_code = "mv"
                break
        
        if not country_code:
            print(f"Warning: No country code found for {country_name}")
            continue
        
        # Add code property to each feature
        for feature in country_geojson['features']:
            if 'properties' not in feature:
                feature['properties'] = {}
            
            feature['properties']['code'] = country_code
            feature['properties']['iso_a2_eh'] = country_code.upper()
            feature['properties']['name'] = country_name
        
        # Add the features to the main GeoJSON
        geojson['features'].extend(country_geojson['features'])
        print(f"Added {country_name} with code {country_code}")
    
    # Save the updated GeoJSON
    with open('custom_countries_with_codes.geo.json', 'w', encoding='utf-8') as f:
        json.dump(geojson, f, ensure_ascii=False)
    
    print(f"Updated GeoJSON saved to custom_countries_with_codes.geo.json")

if __name__ == "__main__":
    # Ensure we're in the correct directory
    if not os.path.exists('../data/world-infos.json'):
        print("Error: world-infos.json not found. Please run this script from the geo directory.")
        exit(1)
    
    if not os.path.exists('countries_with_codes.geo.json'):
        print("Error: countries_with_codes.geo.json not found. Please run this script from the geo directory.")
        exit(1)
    
    if not os.path.exists('other'):
        print("Error: 'other' directory not found. Please run this script from the geo directory.")
        exit(1)
    
    add_missing_countries()