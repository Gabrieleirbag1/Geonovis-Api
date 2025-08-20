#!/usr/bin/env python3
# filepath: /home/gab/GeoNovis/src/assets/geo/check.py

import json
import os

def load_world_infos():
    """Load country data from world-infos.json"""
    with open('/home/gab/GeoNovis/src/assets/data/world-infos.json', 'r', encoding='utf-8') as f:
        world_infos = json.load(f)
    
    # Create a dictionary with country codes as keys and country names as values
    world_countries = {}
    for country in world_infos:
        world_countries[country['flag'].lower()] = country['country']['en']
    
    return world_countries

def load_geojson_countries():
    """Load country data from GeoJSON file"""
    with open('/home/gab/GeoNovis/src/assets/geo/custom_countries_with_codes.geo.json', 'r', encoding='utf-8') as f:
        geojson = json.load(f)
    
    # Create a dictionary with country codes as keys and country names as values
    geojson_countries = {}
    for feature in geojson['features']:
        if 'properties' in feature and 'code' in feature['properties']:
            code = feature['properties']['code'].lower()
            name = feature['properties'].get('name', 'Unknown')
            # Only add if this code hasn't been seen before
            if code not in geojson_countries:
                geojson_countries[code] = name
    
    return geojson_countries

def compare_countries():
    """Compare countries between the two datasets"""
    world_countries = load_world_infos()
    geojson_countries = load_geojson_countries()
    
    print(f"Found {len(world_countries)} countries in world-infos.json")
    print(f"Found {len(geojson_countries)} unique country codes in countries_with_codes.geo.json")
    
    # Find countries in world_infos but not in geojson
    missing_in_geojson = []
    for code, name in world_countries.items():
        if code not in geojson_countries:
            missing_in_geojson.append((code, name))
    
    # Find countries in geojson but not in world_infos
    missing_in_world_infos = []
    for code, name in geojson_countries.items():
        if code not in world_countries:
            missing_in_world_infos.append((code, name))
    
    # Print results
    print("\nCountries in world-infos.json but missing from countries_with_codes.geo.json:")
    if missing_in_geojson:
        for code, name in missing_in_geojson:
            print(f"Code: {code.upper()}, Name: {name}")
    else:
        print("None")
    
    print("\nCountries in countries_with_codes.geo.json but missing from world-infos.json:")
    if missing_in_world_infos:
        for code, name in missing_in_world_infos:
            print(f"Code: {code.upper()}, Name: {name}")
    else:
        print("None")

if __name__ == "__main__":
    # Ensure we're in the correct directory
    if not os.path.exists('../data/world-infos.json'):
        print("Error: world-infos.json not found. Please run this script from the geo directory.")
        exit(1)
    
    if not os.path.exists('countries_with_codes.geo.json'):
        print("Error: countries_with_codes.geo.json not found. Please run this script from the geo directory.")
        exit(1)
    
    compare_countries()