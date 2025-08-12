import VectorSource from 'ol/source/Vector.js';
import OSM from 'ol/source/OSM.js';
import TileLayer from 'ol/layer/Tile.js';
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
import ImageTile from 'ol/source/ImageTile.js';
import TileGrid from 'ol/tilegrid/TileGrid.js';

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
function make_baselayer_source() {
    // Use OSM if a tile layer is not specified
    if (tilelayerurl === '') {
        return new OSM({
            projection: 'EPSG:3857'
        });
    }

    // Create the OS tile source
    const tilegrid = new TileGrid({
        resolutions: [ 896.0, 448.0, 224.0, 112.0, 56.0, 28.0, 14.0, 7.0, 3.5, 1.75 ],
        origin: [ -238375.0, 1376256.0 ]
    });
    return new ImageTile({
        projection: 'EPSG:27700',
        url: tilelayerurl,
        tileGrid: tilegrid,
    })
}

const baselayer = new TileLayer({
    source: make_baselayer_source(),
})

/// Default view that includes Scotland
const view = new View({
    projection: 'EPSG:27700',
    center: fromLonLat([-4.352258, 57.009659], 'EPSG:27700'),
    zoom: 3,
    //resolutions: tilegrid.getResolutions(),
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

//const colorbar_range = [25, 45];

function color_map(value, min, max, values) {
    var scaled_value = (value - min) / (max - min);
    if (scaled_value < 0.0) scaled_value = 0.0;
    if (scaled_value >= 1.0) scaled_value = 0.99;
    return values[ Math.floor(scaled_value * values.length) ]
}

async function update_data_layer(url, colorbar) {
    var data = await fetch_data(url);

    data.features.forEach(function(element) {
        element.properties.data = parseFloat(element.properties.data);
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
            style.getFill().setColor( color_map(feature.values_.data, colorbar.range[0], colorbar.range[1], colorbar.colors) );
        }
        return style;
    };
    
    // Creat the vector layer
    vectorSource = new VectorSource({
        features: new GeoJSON().readFeatures(data),
        //projection: 'EPSG:4326',
    });
    const vectorLayer = new VectorLayer({
        source: vectorSource,
        style: styleFunction,
    });

    // Add to the map
    map.setLayers([baselayer, vectorLayer]);

    // Hookup the opacity slider
    var opacityInput = $("#opacityInput")[0];
    opacityInput.oninput = function() {
        const opacity = parseFloat(opacityInput.value);
        vectorLayer.setOpacity(opacity);
    }
}

function draw_legend(colorbar) {
    for (const svg of $("svg"))
        svg.remove();
    var pos = 0;
    var draw = SVG().addTo("#legend").size(300, 30 * colorbar.colors.length );
    colorbar.colors.slice().reverse().forEach((color_value, _idx, arr) => {
        // Index in original color_values
        const idx = color_values.length - _idx - 1;
        // Add a colored box
        draw.rect(30, 30).move(0, pos).attr({fill: color_value});
        // Add text
        if (idx == color_values.length - 1)
            draw
                .text("> " + colorbar.range[1])
                .move(35, pos);
        else if (idx == 0)
            draw
                .text("< " + colorbar.range[0])
                .move(35, pos);
        else {
            const lower_val = ((idx + 0.0) / colorbar.colors.length) * (colorbar.range[1] - colorbar.range[0]) + colorbar.range[0];
            const upper_val = ((idx + 1.0) / colorbar.colors.length) * (colorbar.range[1] - colorbar.range[0]) + colorbar.range[0];
            draw
                .text(lower_val.toFixed(1) + " - " + upper_val.toFixed(1))
                .move(35, pos);
        }

        pos += 30;
    });
}

const colorbar = {
    extreme_temp: {
        intensity: {
            range: [25, 45],
            colors: color_values,
        },
        return_time: {
            range: [0, 200],
            colors: color_values.slice().reverse(),
        }
    }
};

const selection_tree = {
    extreme_temp: {
        next_choice: "#calculation",
        intensity: {
            "#covariateGroup": true,
            "#calculationGroup": true,
            "#tauReturnGroup": true,
            "#intensityGroup": false,
        },
        return_time: {
            "#covariateGroup": true,
            "#calculationGroup": true,
            "#tauReturnGroup": false,
            "#intensityGroup": true,
        }
    }
};

function update_ui(slider_values) {
    
    const scenario = $("#scenario")[0].value;
    const next_choice = $(selection_tree[scenario].next_choice)[0].value;

    // Update slider visibility
    for (let ui_item_id in selection_tree[scenario][next_choice]) {
        const ui_item = $(ui_item_id)[0];
        const ui_item_is_visible = selection_tree[scenario][next_choice][ui_item_id];
        ui_item.style.display = ui_item_is_visible ? "block" : "none";
    }

    // Update slider labels
    $('#covariateParamLabel').html("Covariate: <span style=\"font-weight:bold\">" + slider_values["#covariateParam"].toFixed(1) + "</span>");
    $('#tauReturnParamLabel').html("Return time: <span style=\"font-weight:bold\">" + slider_values["#tauReturnParam"].toFixed(0) + "</span>");
    $('#intensityParamLabel').html("Intensity: <span style=\"font-weight:bold\">" + slider_values["#intensityParam"].toFixed(0) + "</span>");

    return colorbar[scenario][next_choice] // FIXME
}

function make_data_url(slider_values) {
    const scenario = $("#scenario")[0].value;
    var url_endpoint = new URL("data/" + scenario, window.location.href); 

    if (scenario == "extreme_temp") {

        // Update slider labels
        const calculation = $("#calculation")[0].value;

        url_endpoint.pathname += '/' + calculation;
        url_endpoint.pathname += '/' + slider_values["#covariateParam"];
        if (calculation == "intensity") {
            url_endpoint.pathname += '/' + slider_values["#tauReturnParam"];
        }
        else if(calculation == "return_time") {
            url_endpoint.pathname += '/' + slider_values["#intensityParam"];
        }
    }
    return url_endpoint.href;

}

function get_slider_values() {
    var result = new Object();
    const slider_ids = [
        "#covariateParam",
        "#tauReturnParam",
        "#intensityParam",
    ];

    for (const id of slider_ids) {
        result[id] = parseFloat($(id).val());
    }
    return result;
}

function on_user_input() {
    /// Handler for UI events
    const slider_values = get_slider_values();
    const url_endpoint = make_data_url(slider_values)
    const colorbar = update_ui(slider_values);
    update_data_layer(url_endpoint, colorbar);
    draw_legend(colorbar);
}

$("#covariateParamLabel")[0].value = "Covariate: <span style=\"font-weight:bold\">1.5</span>"; 
$("#covariateParam")[0].oninput = on_user_input;
$("#tauReturnParamLabel")[0].value = "Covariate: <span style=\"font-weight:bold\">100</span>"; 
$("#tauReturnParam")[0].oninput = on_user_input;
$("#intensityParamLabel")[0].value = "Intensity: <span style=\"font-weight:bold\">100</span>"; 
$("#intensityParam")[0].oninput = on_user_input;

$("#scenario")[0].oninput = on_user_input; 
$("#calculation")[0].oninput = on_user_input; 

on_user_input();
