#!/usr/bin/env python3
import json
from pathlib import Path
from lite_logging.lite_logging import log

def merge_geocode_objects(geocode_objects: list[dict]) -> dict:
    """
    Merges multiple geocode objects into a single object with unique keys.
    
    Args:
        geocode_objects (list): List of geocode objects from different regions.
    
    Returns:
        dict: A merged object with unique country codes as keys.
    """
    # Start with an empty result object
    merged_geocode = {}
    
    # Iterate through each object and merge its properties
    for obj in geocode_objects:
        if obj and isinstance(obj, dict) and not isinstance(obj, list):
            merged_geocode.update(obj)
    
    return merged_geocode

def read_geocode_for_region(region: str, base_path: str) -> dict:
    """
    Reads the geocode file for a single region.
    
    Args:
        region (str): Name of the region.
        base_path (str): Path of the geocodes folder.
    
    Returns:
        dict: The geocode object for the region.
    """
    file_path = Path(base_path) / f"{region}-codes.json"
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        log(f"Error reading geocode file for {region}: File not found", level="ERROR")
        return {}
    except json.JSONDecodeError as e:
        log(f"Error parsing geocode file for {region}: {str(e)}", level="ERROR")
        return {}
    except Exception as e:
        log(f"Error reading geocode file for {region}: {str(e)}", level="ERROR")
        return {}

def get_merged_geocodes(regions: list[str], base_path: str) -> dict:
    """
    Returns merged geocodes for the given regions, with unique country codes as keys.
    
    Args:
        regions (list): List of region names.
        base_path (str): Path to the geocodes folder.
    
    Returns:
        dict: The merged geocodes object.
    """
    geocode_objects = [read_geocode_for_region(region, base_path) for region in regions]
    return merge_geocode_objects(geocode_objects)