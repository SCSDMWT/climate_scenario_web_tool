import VectorSource from 'ol/source/Vector.js';
import OSM from 'ol/source/OSM.js';
import Tile from 'ol/layer/Tile.js';
import View from 'ol/View.js'
import Map from 'ol/Map.js'
import Style from 'ol/style/Style.js'
import Fill from 'ol/style/Fill.js'
import VectorLayer from 'ol/layer/Vector.js'
import {fromLonLat} from 'ol/proj';
import {GeoJSON} from 'ol/format';
import $ from 'jquery';

$("#randomParam")[0].value = 0 

var layers = {};

/// The background map
const baselayer = new Tile({
    source: new OSM()
});

/// Default view that includes Scotland
const view = new View({
    center: fromLonLat([-4.352258, 57.009659]),
    zoom: 7,
});

// Source items for the vector layer
var vectorSource = null;

/// The map object
var map = new Map({
    target: 'map',
    layers: [baselayer/*, tmp_layer*/],
    view: view,
});

/// A function to handle browser window resizing.
function resizeMap() {
    const nav_height = document.getElementsByClassName('navbar')[0].clientHeight;

    const mapDiv = document.getElementById('map');
    mapDiv.style.height = window.innerHeight-nav_height + 'px';
    map.updateSize();
}
window.onload = resizeMap;
window.onresize = resizeMap;


/// Request data points 
async function fetch_data(url) {
    let response = await fetch(url);
    let data = await response.json();
    return data
}

var color_values = [
    "#ffffe5",
    "#fff7bc",
    "#fee391",
    "#fec44f",
    "#fe9929",
    "#ec7014",
    "#cc4c02",
    "#993404",
    "#662506",
]; //.reverse()

function color_map(value, min, max, values) {
    var scaled_value = (value - min) / (max - min);
    if (scaled_value < 0.0) scaled_value = 0.0;
    if (scaled_value >= 1.0) scaled_value = 0.99;
    return values[ Math.floor(scaled_value * values.length) ]
}

async function update_data_layer() {
    //const data_url = "http://10.155.55.10?map=/etc/mapserver/scotclimpact.map&service=wfs&version=2.0.0&request=GetFeature&typeNames=grid2&outputFormat=geojson&maxfeatures=10"
    //const data_url = "http://10.155.55.10?map=/etc/mapserver/scotclimpact.map&service=wfs&version=2.0.0&request=GetFeature&typeNames=grid2&outputFormat=geojson"
    //const data_url = mapserverurl + "&service=wfs&version=2.0.0&request=GetFeature&typeNames=grid2&outputFormat=geojson&maxfeatures=10"
    const data_url = mapserverurl + "&service=wfs&version=2.0.0&request=GetFeature&typeNames=grid2&outputFormat=geojson"
    console.log(data_url);
    var data = await fetch_data(data_url);

    data.features.forEach(function(element) {

        element.properties.temp = parseFloat(element.properties.temp);
        element.properties.param_a = parseFloat(element.properties.param_a);
        element.geometry.coordinates[0].forEach( function(coord, idx, arr) { arr[idx] = fromLonLat(coord) } );
    })
    
    const styles = {
        'Polygon': new Style({
            fill: new Fill({
                color: "#11eeee",
            }),
        }),
    };

    const styleFunction = function (feature) {
        var style = styles[feature.getGeometry().getType()];
        if (feature.getGeometry().getType() == 'Polygon') {
            style.getFill().setColor( color_map(feature.values_.temp, -10, 30, color_values) );
        }
        return style;
        //const color = feature.properties.get("param_a", 0);

        //return polygon_style
    };
    
    // Creat the vector layer
    vectorSource = new VectorSource({
        features: new GeoJSON().readFeatures(data),
    });
    const vectorLayer = new VectorLayer({
        source: vectorSource,
        style: styleFunction,
        //projection: 'EPSG:4326',
    });

    // Add to the map
    map.setLayers([baselayer, vectorLayer]);
}

update_data_layer();


$("#randomParam")[0].oninput = function() {
    const slider_value = parseFloat($(this).val());
    $('#randomParamVal').html(slider_value);

    if (!vectorSource)
	return;
    vectorSource.forEachFeature( function(feature) {
	feature.values_.temp = feature.values_.param_a + slider_value;
    });
    vectorSource.changed();
};
