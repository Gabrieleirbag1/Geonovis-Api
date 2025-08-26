#!/usr/bin/env python3
import json
from pathlib import Path
from lite_logging.lite_logging import log

def merge_and_deduplicate_geocodes(geocode_arrays: list[list[dict]], unique_key: str = 'iso') -> list[dict]:
    """
    Merges geocode arrays and removes duplicates.
    
    Args:
        geocode_arrays (list): List of geocode arrays from different regions.
        unique_key (str): Property name to use as unique identifier.
    
    Returns:
        list: Merged array with duplicates removed.
    """
    # Flatten arrays
    merged_geocodes = [item for sublist in geocode_arrays for item in sublist]
    
    # Remove duplicates using dictionary
    unique_map = {}
    
    for geocode in merged_geocodes:
        # Get a unique identifier, falling back to JSON string if key doesn't exist
        if unique_key in geocode:
            key = geocode[unique_key]
        else:
            key = json.dumps(geocode, sort_keys=True)
        
        unique_map[key] = geocode
    
    return list(unique_map.values())

def read_and_merge_geocode_files(regions: list[str], base_path: str) -> list[dict]:
    """
    Reads geocode files for multiple regions.
    
    Args:
        regions (list): List of region names.
        base_path (str): Base path to geocode files.
    
    Returns:
        list: Merged geocode data.
    """
    geocode_arrays = []
    
    for region in regions:
        file_path = Path(base_path) / f"{region}.json"
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                geocodes = json.load(f)
                geocode_arrays.append(geocodes)
        except FileNotFoundError:
            log(f"Warning: Could not read geocode file for {region}: File not found", level="WARNING")
            geocode_arrays.append([])
        except json.JSONDecodeError as e:
            log(f"Error parsing geocode file for {region}: {str(e)}", level="ERROR")
            geocode_arrays.append([])
        except Exception as e:
            log(f"Error reading geocode file for {region}: {str(e)}", level="ERROR")
            geocode_arrays.append([])
    
    return merge_and_deduplicate_geocodes(geocode_arrays)