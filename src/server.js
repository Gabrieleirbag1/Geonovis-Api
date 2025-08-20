const express = require('express');
const bodyParser = require('body-parser');
const cors = require('cors');

const app = express();
const port = 3100;

app.use(cors());
app.use(bodyParser.json());

app.listen(port, () => {
  console.log(`Server is running on http://localhost:${port}`);
});