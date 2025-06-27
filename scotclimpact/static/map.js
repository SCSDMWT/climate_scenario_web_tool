//import VectorSource from 'ol/source/Vector.js';

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

async function update_data_layer() {
    //const data_url = "http://10.155.55.10?map=/etc/mapserver/scotclimpact.map&service=wfs&version=2.0.0&request=GetFeature&typeNames=grid2&outputFormat=geojson&maxfeatures=10"
    const data_url = "http://10.155.55.10?map=/etc/mapserver/scotclimpact.map&service=wfs&version=2.0.0&request=GetFeature&typeNames=grid2&outputFormat=geojson"
    data = await fetch_data(data_url);


    data.features.forEach(function(element, idx, arr) {
        element.geometry.coordinates = ol.proj.fromLonLat(element.geometry.coordinates);
    })

    console.log(data);

    // Set the style 
    const image = new ol.style.Circle({
        radius: 5,
        fill: null,
        stroke: new ol.style.Stroke({color: 'red', width: 1}),
    });

    const styles = {
        'Point': new ol.style.Style({
            image: image,
        }),
    };

    const styleFunction = function (feature) {
        return styles[feature.getGeometry().getType()];
    };
    
    // Creat the vector layer
    const vectorSource = new ol.source.Vector({
        features: new ol.format.GeoJSON().readFeatures(data),
    });
    vectorSource.addFeature(new ol.Feature(new ol.geom.Circle([5e6, 7e6], 1e6)));
    const vectorLayer = new ol.layer.Vector({
        source: vectorSource,
        style: styleFunction,
        //projection: 'EPSG:4326',
    });

    vectorLayer.projection = "EPSG:4326";
    // Add to the map
    map.setLayers([baselayer, vectorLayer]);
}

update_data_layer();
