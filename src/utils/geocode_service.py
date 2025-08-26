#!/usr/bin/env python3
# filepath: /home/gab/Geonovis-Api/src/utils/geocode_service.py
import json
import os
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

def merge_geocode_objects(geocode_objects):
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

def read_geocode_for_region(region, base_path):
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
        logger.error(f"Error reading geocode file for {region}: File not found")
        return {}
    except json.JSONDecodeError as e:
        logger.error(f"Error parsing geocode file for {region}: {str(e)}")
        return {}
    except Exception as e:
        logger.error(f"Error reading geocode file for {region}: {str(e)}")
        return {}

def get_merged_geocodes(regions, base_path):
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