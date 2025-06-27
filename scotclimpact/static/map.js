
var layers = {};

/// The background map
const baselayer = new ol.layer.Tile({
    source: new ol.source.OSM()
});

/// The temperature layer
const tmp_layer = new ol.layer.Tile({
    source: new ol.source.TileWMS({
        url: mapserverurl,
        params : {
            'LAYERS': 'grid2'
        },
        crossOrigin: 'anonymous',
        transition: 0,
    })
})

/// Default view that includes Scotland
const view = new ol.View({
    center: ol.proj.fromLonLat([-4.352258, 57.009659]),
    zoom: 7
});

/// The map object
var map = new ol.Map({
    target: 'map',
    layers: [baselayer, tmp_layer],
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
