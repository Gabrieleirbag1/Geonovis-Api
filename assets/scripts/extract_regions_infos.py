import json
import os
from pathlib import Path

def main():
    # Get the directory where the script is located
    script_dir = Path(__file__).parent.absolute()
    
    # Define paths relative to the script location
    world_infos_path = os.path.join(script_dir, "..", "data", "regions", "world-infos.json")
    major_regions_path = os.path.join(script_dir, "..", "data", "regions", "majorRegions.json")
    output_dir = os.path.join(script_dir, "..", "data", "regions", "majorRegions")
    
    # Create the output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Load the world-infos.json file
    with open(world_infos_path, "r", encoding="utf-8") as f:
        world_infos = json.load(f)
    
    # Load the majorRegions.json file
    with open(major_regions_path, "r", encoding="utf-8") as f:
        major_regions = json.load(f)
    
    # Create a mapping from country codes to world-infos entries
    country_code_map = {}
    for country in world_infos:
        if "flag" in country:
            country_code_map[country["flag"].lower()] = country
    
    # For each major region, create a filtered version of world-infos
    for region_key, region_data in major_regions["majorsRegions"].items():
        if "countries" not in region_data:
            print(f"Warning: No countries data for region {region_key}")
            continue
            
        region_countries = []
        region_codes = [code.lower() for code in region_data["countries"]["code"]]
        
        # Filter the world_infos to include only countries in this region
        for code in region_codes:
            if code in country_code_map:
                region_countries.append(country_code_map[code])
            else:
                print(f"Warning: Country code {code} not found in world-infos.json")
        
        # Save the filtered data to a new file
        output_file = os.path.join(output_dir, f"{region_key}-infos.json")
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(region_countries, f, ensure_ascii=False, indent=2)
        
        print(f"Generated {output_file} with {len(region_countries)} countries")

if __name__ == "__main__":
    main()