import json
import os

def filter_geojson_by_country_codes():
    # Load the world-infos.json file
    with open('/home/frigiel/Documents/VSCODE/Angular/GeoNovis/src/assets/data/world-infos.json', 'r', encoding='utf-8') as f:
        world_infos = json.load(f)
    
    # Extract country codes (flags) from world-infos.json and convert to uppercase for comparison
    valid_codes = set(country_info['flag'].upper() for country_info in world_infos)
    
    # Load the original GeoJSON file
    with open('/home/frigiel/Documents/VSCODE/Angular/GeoNovis/src/assets/geo/custom3.geo.json', 'r', encoding='utf-8') as f:
        geojson_data = json.load(f)
    
    # Filter features based on iso_a2_eh codes
    filtered_features = []
    removed_features = []
    
    for feature in geojson_data['features']:
        iso_code = feature.get('properties', {}).get('iso_a2_eh', '')
        
        # Convert to uppercase for case-insensitive comparison
        if iso_code.upper() in valid_codes:
            filtered_features.append(feature)
        else:
            removed_features.append({
                'iso_code': iso_code,
                'name': feature.get('properties', {}).get('name', 'Unknown')
            })
    
    # Create the new filtered GeoJSON
    filtered_geojson = geojson_data.copy()
    filtered_geojson['features'] = filtered_features
    
    # Save the filtered GeoJSON to a new file
    output_file = 'filtered_custom3.geo.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(filtered_geojson, f, ensure_ascii=False, indent=2)
    
    # Print summary
    print(f"Original features count: {len(geojson_data['features'])}")
    print(f"Filtered features count: {len(filtered_features)}")
    print(f"Removed {len(removed_features)} features")
    
    if removed_features:
        print("\nRemoved features:")
        for item in removed_features:
            print(f"  - {item['name']} (ISO code: {item['iso_code']})")
    
    print(f"\nFiltered GeoJSON saved to: {output_file}")

if __name__ == "__main__":
    filter_geojson_by_country_codes()