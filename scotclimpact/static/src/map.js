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
import { SVG } from '@svgdotjs/svg.js'
import proj4 from 'proj4';
import {get as getProjection} from 'ol/proj.js';
import {register} from 'ol/proj/proj4.js';

/// Setup the British National Grid projection
// See: https://openlayers.org/doc/tutorials/raster-reprojection.html
proj4.defs('EPSG:27700', '+proj=tmerc +lat_0=49 +lon_0=-2 +k=0.9996012717 ' +
    '+x_0=400000 +y_0=-100000 +ellps=airy ' +
    '+towgs84=446.448,-125.157,542.06,0.15,0.247,0.842,-20.489 ' +
    '+units=m +no_defs');
register(proj4);
const proj27700 = getProjection('EPSG:27700');
proj27700.setExtent([0, 0, 700000, 1300000]);

/// The background map
const baselayer = new Tile({
    source: new OSM({
        projection: 'EPSG:3857'
    })
});

/// Default view that includes Scotland
const view = new View({
    projection: 'EPSG:27700',
    center: fromLonLat([-4.352258, 57.009659], 'EPSG:27700'),
    zoom: 3,
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

const color_values = [
    "#ffffe5",
    "#fff7bc",
    "#fee391",
    "#fec44f",
    "#fe9929",
    "#ec7014",
    "#cc4c02",
    "#993404",
    "#662506",
];

const colorbar_range = [-10, 30];

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
            style.getFill().setColor( color_map(feature.values_.temp, colorbar_range[0], colorbar_range[1], color_values) );
        }
        return style;
        //const color = feature.properties.get("param_a", 0);

        //return polygon_style
    };
    
    // Creat the vector layer
    vectorSource = new VectorSource({
        features: new GeoJSON().readFeatures(data),
        projection: 'EPSG:4326',
    });
    const vectorLayer = new VectorLayer({
        source: vectorSource,
        style: styleFunction,
    });

    // Add to the map
    map.setLayers([baselayer, vectorLayer]);

    // Hookup the opacity offset
    var opacityInput = $("#opacityInput")[0];
    opacityInput.oninput = function() {
        const opacity = parseFloat(opacityInput.value);
        vectorLayer.setOpacity(opacity);
    }
}

function add_legend() {
    var pos = 0;
    var draw = SVG().addTo("#legend").size(300, 30 * color_values.length );
    color_values.slice().reverse().forEach((color_value, _idx, arr) => {
        // Index in original color_values
        const idx = color_values.length - _idx - 1;
        // Add a colored box
        draw.rect(30, 30).move(0, pos).attr({fill: color_value});
        // Add text
        if (idx == color_values.length - 1)
            draw
                .text("> " + colorbar_range[1])
                .move(35, pos);
        else if (idx == 0)
            draw
                .text("< " + colorbar_range[0])
                .move(35, pos);
        else {
            const lower_val = ((idx + 0.0) / color_values.length) * (colorbar_range[1] - colorbar_range[0]) + colorbar_range[0];
            const upper_val = ((idx + 1.0) / color_values.length) * (colorbar_range[1] - colorbar_range[0]) + colorbar_range[0];
            draw
                .text(lower_val.toFixed(1) + " - " + upper_val.toFixed(1))
                .move(35, pos);
        }

        pos += 30;
    });
}

update_data_layer();
add_legend();


//$("#offsetParam")[0].value = 0 
$("#offsetParamLabel")[0].value = "Add an offset: <span style=\"font-weight:bold\">0</span>"; 
$("#offsetParam")[0].oninput = function() {
    const slider_value = parseFloat($(this).val());
    $('#offsetParamLabel').html("Add an offset: <span style=\"font-weight:bold\">" + slider_value.toFixed(1) + "</span>");

    if (!vectorSource)
	return;
    vectorSource.forEachFeature( function(feature) {
	feature.values_.temp = feature.values_.param_a + slider_value;
    });
    vectorSource.changed();
};

