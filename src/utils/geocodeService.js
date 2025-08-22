const fs = require('fs');
const path = require('path');

/**
 * Merges multiple geocode objects into a single object with unique keys.
 * @param {Array<Object>} geocodeObjects - Array of geocode objects from different regions.
 * @returns {Object} - A merged object with unique country codes as keys.
 */
function mergeGeocodeObjects(geocodeObjects) {
  // Start with an empty result object
  const mergedGeocode = {};
  
  // Iterate through each object and merge its properties
  geocodeObjects.forEach(obj => {
    if (obj && typeof obj === 'object' && !Array.isArray(obj)) {
      Object.assign(mergedGeocode, obj);
    }
  });
  
  return mergedGeocode;
}

/**
 * Reads the geocode file for a single region.
 * @param {string} region - Name of the region.
 * @param {string} basePath - Path of the geocodes folder.
 * @returns {Promise<Object>} - Promise that resolves to the geocode object for the region.
 */
function readGeocodeForRegion(region, basePath) {
  return new Promise((resolve) => {
    const filePath = path.join(basePath, `${region}-codes.json`);
    fs.readFile(filePath, 'utf8', (err, data) => {
      if (err) {
        console.error(`Error reading geocode file for ${region}: ${err.message}`);
        return resolve({});
      }
      try {
        const geocodes = JSON.parse(data);
        resolve(geocodes);
      } catch (parseErr) {
        console.error(`Error parsing geocode file for ${region}: ${parseErr.message}`);
        resolve({});
      }
    });
  });
}

/**
 * Returns merged geocodes for the given regions, with unique country codes as keys.
 * @param {Array<string>} regions - Array of region names.
 * @param {string} basePath - Path to the geocodes folder.
 * @returns {Promise<Object>} - Promise that resolves to the merged geocodes object.
 */
function getMergedGeocodes(regions, basePath) {
  const readPromises = regions.map(region => readGeocodeForRegion(region, basePath));
  return Promise.all(readPromises)
    .then(geocodeObjects => mergeGeocodeObjects(geocodeObjects));
}

module.exports = { getMergedGeocodes };