//import VectorSource from 'ol/source/Vector.js';

$("#randomParam")[0].value = 0 

var layers = {};

/// The background map
const baselayer = new ol.layer.Tile({
    source: new ol.source.OSM()
});

/// The temperature layer
//const tmp_layer = new ol.layer.Tile({
//    source: new ol.source.TileWMS({
//        url: mapserverurl,
//        params : {
//            'LAYERS': 'grid2'
//        },
//        crossOrigin: 'anonymous',
//        transition: 0,
//    })
//})

/// Default view that includes Scotland
const view = new ol.View({
    center: ol.proj.fromLonLat([-4.352258, 57.009659]),
    zoom: 7,
    //center: [-4.352258, 57.009659],
    //projection: 'EPSG:4326',
});

// Source items for the vector layer
var vectorSource = null;

/// The map object
var map = new ol.Map({
    target: 'map',
    layers: [baselayer/*, tmp_layer*/],
    //overlays: [overlayHist, overlayQual],
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

color_values = [
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
    data = await fetch_data(data_url);
    console.log(data);

    //const delta = 0.004;

    
    data.features.forEach(function(element) {

	element.properties.temp = parseFloat(element.properties.temp);
	element.properties.param_a = parseFloat(element.properties.param_a);
        element.geometry.coordinates[0].forEach( function(coord, idx, arr) { arr[idx] = ol.proj.fromLonLat(coord) } );
        //element.geometry.coordinates =
        //    ol.proj.fromLonLat(element.geometry.coordinates);
        
        //element.geometry.type = "Polygon";
        //element.geometry.coordinates = [
        //    ol.proj.fromLonLat([element.geometry.coordinates[0]-delta, element.geometry.coordinates[1]-delta]),
        //    ol.proj.fromLonLat([element.geometry.coordinates[0]+delta, element.geometry.coordinates[1]-delta]),
        //    ol.proj.fromLonLat([element.geometry.coordinates[0]+delta, element.geometry.coordinates[1]+delta]),
        //    ol.proj.fromLonLat([element.geometry.coordinates[0]-delta, element.geometry.coordinates[1]+delta]),
        //];
    })
    

    //console.log(data);

    // Set the style 
    const image = new ol.style.Circle({
        radius: 5,
        fill: null,
        stroke: new ol.style.Stroke({color: 'red', width: 1}),
    });

    //const polygon_style = new ol.style.Style({
    //    fill: new ol.style.Fill({
    //        color: "#11eeee",
    //    })
    //});
    const styles = {
        'Point': new ol.style.Style({
            image: image,
        }),
        'Polygon': new ol.style.Style({
            fill: new ol.style.Fill({
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
    vectorSource = new ol.source.Vector({
        features: new ol.format.GeoJSON().readFeatures(data),
    });
    const vectorLayer = new ol.layer.Vector({
        source: vectorSource,
        style: styleFunction,
        //projection: 'EPSG:4326',
    });

    //vectorLayer.projection = "EPSG:4326";
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
