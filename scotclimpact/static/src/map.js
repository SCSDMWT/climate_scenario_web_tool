import VectorSource from 'ol/source/Vector.js';
import OSM from 'ol/source/OSM.js';
import TileLayer from 'ol/layer/Tile.js';
import View from 'ol/View.js'
import Map from 'ol/Map.js'
import Style from 'ol/style/Style.js'
import Fill from 'ol/style/Fill.js'
import Stroke from 'ol/style/Stroke.js'
import VectorLayer from 'ol/layer/Vector.js'
import {fromLonLat} from 'ol/proj';
import {GeoJSON} from 'ol/format';
import proj4 from 'proj4';
import {get as getProjection} from 'ol/proj.js';
import {register} from 'ol/proj/proj4.js';
import ImageTile from 'ol/source/ImageTile.js';
import TileGrid from 'ol/tilegrid/TileGrid.js';
import Text from 'ol/style/Text.js';
import tinycolor from "tinycolor2";

import {apply_color_map} from "../src/color_map.js";

/// Setup the British National Grid projection
// See: https://openlayers.org/doc/tutorials/raster-reprojection.html
proj4.defs('EPSG:27700', '+proj=tmerc +lat_0=49 +lon_0=-2 +k=0.9996012717 ' +
           '+x_0=400000 +y_0=-100000 +ellps=airy ' +
           '+towgs84=446.448,-125.157,542.06,0.15,0.247,0.842,-20.489 ' +
           '+units=m +no_defs');
register(proj4);
const proj27700 = getProjection('EPSG:27700');
proj27700.setExtent([0, 0, 700000, 1300000]);

/// A class to wrap OpenLayers objects
export class UIMap {
    #layers = [null, null, null, null];
    #base_layer_idx = 0;
    #data_layer_idx = 1;
    #boundary_layer_idx = 2;
    #selection_layer_idx = 3;
    #map = null;
    #selection = {};

    constructor(div_id, tilelayerurl) {
        /// Default view that includes Scotland
        const view = new View({
            projection: 'EPSG:27700',
            center: fromLonLat([-4.352258, 57.009659], 'EPSG:27700'),
            zoom: 3,
            //resolutions: tilegrid.getResolutions(),
        });

        this.#map = new Map({
            target: div_id,
            layers: [],
            view: view,
        });

        window.onload = () => this.resizeMap();
        window.onresize = () => this.resizeMap();
        this.make_baselayer(tilelayerurl);
    }

    /// Adds the background map
    make_baselayer(tilelayerurl) {
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

        this.#layers[this.#base_layer_idx] = new TileLayer({
            source: make_baselayer_source(),
        });
        this.update_layers()
        this.init_selection_events();
    }

    /// Register event listeners for clicking on the data layer
    init_selection_events() {
        this.#map.on(['click'], (event) => {
            const data_layer = this.#layers[this.#data_layer_idx];
            if (!data_layer) {
                return;
            }

            data_layer.getFeatures(event.pixel).then((features) => {
                if (!features.length) {
                    this.#selection = {};
                    this.#layers[this.#selection_layer_idx].changed();
                    return;
                }

                const feature = features[0];
                if (!feature)
                    return;

                this.#selection = {};
                this.#selection[feature.ol_uid] = feature;
                    
                this.#layers[this.#selection_layer_idx].changed();
            });
        });
    }
    /// Adds the selection layer to the map
    update_selection_layer(data_layer, data_layer_source) {
        this.#layers[this.#selection_layer_idx] = new VectorLayer({
            source: data_layer_source,
            style: (feature) => {
                if (!(feature.ol_uid in this.#selection)) 
                    return;

                const selected_style = data_layer.styleFunction_(feature);
                //const stroke = selected_style.getStroke();
                const fill = selected_style.getFill();
                const fill_color = tinycolor(fill.getColor());
                const selection_color = 
                    fill_color.isDark() 
                    ? "#eeeeee" //fill_color.complement().brighten(20).toHexString()
                    : "#111111" //fill_color.complement().brighten(-20).toHexString()
                ;
                return new Style({
                    stroke: new Stroke({ 
                        color: selection_color,
                        width: 4,
                    }),
                });

            }
        })
    }

    /// A method to handle browser window resizing.
    resizeMap() {
        const nav_height = document.getElementsByClassName('navbar')[0].clientHeight;

        const mapDiv = document.getElementById('map');
        mapDiv.style.height = window.innerHeight-nav_height + 'px';
        this.#map.updateSize();
    }

    /// Update the values shown in the data layer.
    update_data_layer(data, colorbar) {
        //var data = await fetch_data(url);

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
                const color_value = apply_color_map(feature.values_.data, colorbar.edges, colorbar.colors, colorbar.endpoint_type);
                //console.log(feature.values_.data, color_value);
                style.getFill().setColor(color_value);
            }
            return style;
        };

        // Update the vector layer
        const vectorSource = new VectorSource({
            features: new GeoJSON().readFeatures(data),
        });
        this.#layers[this.#data_layer_idx] = new VectorLayer({
            source: vectorSource,
            style: styleFunction,
        });

        this.update_selection_layer(this.#layers[this.#data_layer_idx], vectorSource);
        // Reset the map layers
        this.update_layers()
    }

    set_data_layer_opacity(opacity) {
        this.#layers[this.#data_layer_idx] && this.#layers[this.#data_layer_idx].setOpacity(opacity);
    }

    show_spinner() {
        console.log('show spinner')
        this.#map.getTargetElement().classList.add('spinner');
    }

    update_boundary_layer(data, get_text_func) {

        function create_stroke() {
            return new Stroke({
                color: "#000000",
            })
        };
        function create_text(feature) {
            const font =  'bold 10pt/1 Verdana';
            return new Text({
                font: font,
                text: get_text_func(feature),
                fill: new Fill({color: "#000000"}),
                stroke: new Stroke({color: "#eeeeee", width: 1}),
            });
        }
        function create_style(feature) {
            return new Style({
                stroke: create_stroke(),
                text: create_text(feature),
            })
        }

        const styles = {
            'Polygon': create_style,
            'MultiPolygon': create_style,
        };

        const styleFunction = function (feature) {
            const style_func = styles[feature.getGeometry().getType()];
            return style_func(feature);
        };

        // Creat the vector layer
        const vectorSource = new VectorSource({
            features: new GeoJSON().readFeatures(data),
        });

        // Add to the map
        this.#layers[this.#boundary_layer_idx] = new VectorLayer({
            source: vectorSource,
            style: styleFunction,
        });

        // Reset the map layers
        this.update_layers()
    }

    update_layers() {
        this.#map.setLayers(
            this.#layers.filter( (layer) => layer )
        );
    }

    hide_boundary_layer() {
        this.#layers[this.#boundary_layer_idx] = null;
        this.update_layers();
    }
}
