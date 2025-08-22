import json
import os
from pathlib import Path

def main():
    # Get the directory where the script is located
    script_dir = Path(__file__).parent.absolute()
    
    # Define paths relative to the script location
    world_infos_path = os.path.join(script_dir, "..", "data", "regions", "world-infos.json")
    output_dir = os.path.join(script_dir, "..", "data", "regions", "regions", "continents")
    
    # Create the output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Load the world-infos.json file
    with open(world_infos_path, "r", encoding="utf-8") as f:
        world_infos = json.load(f)
    
    # Initialize continent dictionaries to store countries by continent
    continents = {
        "europe": {"name": {"en": "Europe", "fr": "Europe"}, "countries": []},
        "asia": {"name": {"en": "Asia", "fr": "Asie"}, "countries": []},
        "africa": {"name": {"en": "Africa", "fr": "Afrique"}, "countries": []},
        "north_america": {"name": {"en": "North America", "fr": "Amérique du Nord"}, "countries": []},
        "south_america": {"name": {"en": "South America", "fr": "Amérique du Sud"}, "countries": []},
        "oceania": {"name": {"en": "Oceania", "fr": "Océanie"}, "countries": []},
        "antarctica": {"name": {"en": "Antarctica", "fr": "Antarctique"}, "countries": []}
    }
    
    # French to English continent name mapping for lookup
    fr_to_en = {
        "Europe": "europe",
        "Asie": "asia",
        "Afrique": "africa",
        "Amérique du Nord": "north_america",
        "Amérique du Sud": "south_america",
        "Océanie": "oceania",
        "Antarctique": "antarctica"
    }
    
    # Group countries by continent
    for country in world_infos:
        if "continent" in country and "fr" in country["continent"]:
            continent_fr = country["continent"]["fr"]
            
            if continent_fr in fr_to_en:
                continent_key = fr_to_en[continent_fr]
                continents[continent_key]["countries"].append(country)
            else:
                print(f"Unknown continent: {continent_fr}")
    
    # Save each continent's data to a separate file
    for continent_key, continent_data in continents.items():
        if len(continent_data["countries"]) > 0:
            output_file = os.path.join(output_dir, f"{continent_key}-infos.json")
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(continent_data["countries"], f, ensure_ascii=False, indent=2)
            
            print(f"Generated {output_file} with {len(continent_data['countries'])} countries")

if __name__ == "__main__":
    main()