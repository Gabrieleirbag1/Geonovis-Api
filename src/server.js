const express = require('express');
const bodyParser = require('body-parser');
const cors = require('cors');
const fs = require('fs');
const path = require('path');
const geocodeService = require('./utils/geocodeService');

const app = express();
const port = 3111;

app.use(cors());
app.use(bodyParser.json());

app.get('/', (req, res) => {
  res.send('Welcome to the Geonovis API!');
});

app.get('/api/geojson/:region', (req, res) => {
  const region = req.params.region;
  const filePath = path.join(__dirname, '..', 'assets', 'geo', region, `${region}.geo.json`);
  fs.access(filePath, fs.constants.F_OK, (err) => {
    if (err) {
      console.error(`Error: File not found - ${filePath}`);
      return res.status(404).json({ 
        error: 'Region file not found',
        details: `Could not find ${region}.geojson in assets/${region}/`
      });
    }
    
    res.sendFile(filePath, (err) => {
      if (err) {
        console.error(`Error sending file: ${err.message}`);
        res.status(err.status || 500).end();
      } else {
        console.log(`Sent: ${region}.geo.json`);
      }
    });
  });
});

app.get('/api/geocodes', (req, res) => {
  const regions = req.query.regions;
  if (!regions) {
    return res.status(400).json({
      error: 'Missing regions parameter',
      details: 'Please provide a regions parameter with a comma-separated list of region names'
    });
  }
  
  const regionList = regions.split(',').map(region => region.trim());
  const geocodesBasePath = path.join(__dirname, '..', 'assets', 'geocodes');
  
  geocodeService.getMergedGeocodes(regionList, geocodesBasePath)
    .then(uniqueGeocodes => {
      res.json(uniqueGeocodes);
    })
    .catch(err => {
      console.error(`Error processing geocodes: ${err.message}`);
      res.status(500).json({
        error: 'Failed to process geocodes',
        details: err.message
      });
    });
});

app.listen(port, () => {
  console.log(`Server is running on http://localhost:${port}`);
});