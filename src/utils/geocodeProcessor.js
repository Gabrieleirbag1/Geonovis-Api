/**
 * Processes and merges geocode data from multiple regions
 * removing duplicate entries
 */

/**
 * Merges geocode arrays and removes duplicates
 * @param {Array<Array>} geocodeArrays - Array of geocode arrays from different regions
 * @param {string} uniqueKey - Property name to use as unique identifier (default: 'iso')
 * @returns {Array} - Merged array with duplicates removed
 */
function mergeAndDeduplicateGeocodes(geocodeArrays, uniqueKey = 'iso') {
  // Flatten arrays
  const mergedGeocodes = [].concat(...geocodeArrays);
  
  // Remove duplicates using Map
  const uniqueMap = new Map();
  
  mergedGeocodes.forEach(geocode => {
    // Get a unique identifier, falling back to stringification if key doesn't exist
    const key = geocode[uniqueKey] || JSON.stringify(geocode);
    uniqueMap.set(key, geocode);
  });
  
  return Array.from(uniqueMap.values());
}

/**
 * Reads geocode files for multiple regions
 * @param {Array<string>} regions - Array of region names
 * @param {string} basePath - Base path to geocode files
 * @returns {Promise<Array>} - Promise resolving to merged geocode data
 */
function readAndMergeGeocodeFiles(regions, basePath, fs, path) {
  return Promise.all(
    regions.map(region => {
      return new Promise((resolve, reject) => {
        const filePath = path.join(basePath, `${region}.json`);
        fs.readFile(filePath, 'utf8', (err, data) => {
          if (err) {
            console.warn(`Warning: Could not read geocode file for ${region}: ${err.message}`);
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
    })
  ).then(geocodeArrays => mergeAndDeduplicateGeocodes(geocodeArrays));
}

module.exports = {
  mergeAndDeduplicateGeocodes,
  readAndMergeGeocodeFiles
};