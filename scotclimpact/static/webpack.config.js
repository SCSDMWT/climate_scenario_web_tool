const path = require('path');

module.exports = {
  mode: 'development',
  entry: './src/map.js',
  output: {
    filename: 'map.js',
    path: path.resolve(__dirname, 'dist'),
  },
  module: {
    //rules: [{ test: /\.js$/, use: 'raw-loader' }],
  },
};
