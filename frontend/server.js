// Author: Hassan Wahba

const express = require('express');
const serveStatic = require('serve-static');
const path = require('path');

const app = express();

// Serve the static files in the dist directory
app.use(serveStatic(path.join(__dirname, 'dist')));

// Catch all routes and redirect to the index.html
app.get('*', function (req, res) {
  res.sendFile(__dirname + '/dist/index.html');
});

// Choose the port and start the server
const PORT = process.env.PORT || 8080;
app.listen(PORT, () => {
  console.log(`Server is running on port ${PORT}`);
});
