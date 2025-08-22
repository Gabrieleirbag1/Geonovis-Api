const fs = require('fs');
const path = require('path');

/**
 * Merges arrays and removes duplicate geocodes based on a unique identifier.
 * @param {Array<Array>} geocodeArrays - Array of geocode arrays from different regions
 * @param {string} uniqueKey - Property name to use as unique identifier (default: 'iso')
 * @returns {Array} - Merged array with duplicates removed
 */
function mergeAndDeduplicateGeocodes(geocodeArrays, uniqueKey = 'iso') {
    const mergedGeocodes = [].concat(...geocodeArrays);
    const uniqueMap = new Map();
    mergedGeocodes.forEach(geocode => {
        const key = geocode[uniqueKey] || JSON.stringify(geocode);
        uniqueMap.set(key, geocode);
    });
    return Array.from(uniqueMap.values());
}

/**
 * Reads the geocode file for a single region.
 * @param {string} region - Name of the region
 * @param {string} basePath - Path of the geocodes folder
 * @returns {Promise<Array>} - Returns a promise that resolves to the geocode array for the region.
 */
function readGeocodeForRegion(region, basePath) {
    return new Promise((resolve) => {
        // Our geocode files follow the pattern: region-codes.json
        const filePath = path.join(basePath, `${region}-codes.json`);
        fs.readFile(filePath, 'utf8', (err, data) => {
            if (err) {
                console.error(`Error reading geocode file for ${region}: ${err.message}`);
                return resolve([]);
            }
            try {
                const geocodes = JSON.parse(data);
                resolve(geocodes);
            } catch (parseErr) {
                console.error(`Error parsing geocode file for ${region}: ${parseErr.message}`);
                resolve([]);
            }
        });
    });
}

/**
 * Returns merged and deduplicated geocodes for the given regions.
 * @param {Array<string>} regions - Array of region names
 * @param {string} basePath - Path to the geocodes folder
 * @returns {Promise<Array>} - Promise that resolves to the merged geocodes array.
 */
function getMergedGeocodes(regions, basePath) {
    const readPromises = regions.map(region => readGeocodeForRegion(region, basePath));
    return Promise.all(readPromises)
        .then(geocodeArrays => mergeAndDeduplicateGeocodes(geocodeArrays));
}

module.exports = { getMergedGeocodes };