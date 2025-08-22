const express = require('express');
const bodyParser = require('body-parser');
const cors = require('cors');
const fs = require('fs');
const path = require('path');

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
  // Check if file exists before trying to send it
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
        console.log(`Sent: ${region}.geojson`);
      }
    });
  });
});

app.listen(port, () => {
  console.log(`Server is running on http://localhost:${port}`);
});