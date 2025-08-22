import json
import os
from pathlib import Path
import glob

def main():
    # Get the directory where the script is located
    script_dir = Path(__file__).parent.absolute()
    
    # Define paths relative to the script location
    continents_dir = os.path.join(script_dir, "..", "data", "regions", "continents")
    major_regions_dir = os.path.join(script_dir, "..", "data", "regions", "majorRegions")
    world_codes_path = os.path.join(script_dir, "..", "data", "world-codes.json")
    
    # Load the world-codes.json file as a template
    with open(world_codes_path, "r", encoding="utf-8") as f:
        world_codes = json.load(f)
    
    # Process both directories
    directories = [continents_dir, major_regions_dir]
    for directory in directories:
        if os.path.exists(directory):
            process_directory(directory, world_codes)
            print(f"Processed directory: {directory}")
        else:
            print(f"Directory not found: {directory}")
    
    print("All region code files generated successfully.")

def process_directory(directory, world_codes):
    # Find all *-infos.json files in the directory
    info_files = glob.glob(os.path.join(directory, "*-infos.json"))
    
    for info_file in info_files:
        # Generate the corresponding codes file name
        basename = os.path.basename(info_file)
        region_name = basename.replace("-infos.json", "")
        codes_file = os.path.join(os.path.dirname(info_file), f"{region_name}-codes.json")
        
        # Load the region info file to get country codes
        with open(info_file, "r", encoding="utf-8") as f:
            region_info = json.load(f)
        
        # Create a new codes object with only the countries in this region
        region_codes = {}
        
        # Extract country codes from the region info file
        country_codes = []
        for country in region_info:
            if "flag" in country:
                country_code = country["flag"].lower()
                country_codes.append(country_code)
        
        # Create the region-specific codes dictionary
        for country_code in country_codes:
            if country_code in world_codes:
                # Copy the structure from world-codes for this country
                region_codes[country_code] = {
                    "code": country_code,
                    "found": None,
                    "turn": False,
                    "selected": False
                }
            else:
                print(f"Warning: Country code {country_code} not found in world-codes.json")
        
        # Save the region codes to a new file
        with open(codes_file, "w", encoding="utf-8") as f:
            json.dump(region_codes, f, ensure_ascii=False, indent=2)
        
        print(f"Generated {codes_file} with {len(region_codes)} country codes")

if __name__ == "__main__":
    main()