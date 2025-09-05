const path = require('path');

module.exports = {
  mode: 'development',
  entry: {
      main: './src/main.js',
      disclaimer: './src/disclaimer.js',
  },
  output: {
    filename: '[name].js',
    path: path.resolve(__dirname, 'dist'),
  },
  module: {
    rules: [
    ],
  },
};
