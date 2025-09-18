import $ from 'jquery';
import Cookies from "js-cookie";

import {apply_color_map, legend_endpoints} from "../src/color_map.js";
import {draw_legend} from "../src/legend.js";
import {UIMap} from "../src/map.js";

function check_disclaimer_cookie() {
    /// Redirects to the disclaimer page if the ToS have not been accepted.
    if (!Cookies.get('accepted_tos')) {
        window.location.replace(window.location.href + '/disclaimer');
    }
}

const colorbar = {
    extreme_temp: {
        intensity: {
            edges: [25, 27, 29, 31, 33, 35, 37, 39],
            // Colorbrewer YlOrBr-9
            colors: ["#ffffe5", "#fff7bc", "#fee391", "#fec44f", "#fe9929", "#ec7014", "#cc4c02", "#993404", "#662506"],
            // Colorbrewer YlOrBr-8
            //colors: ["#ffffe5", "#fff7bc", "#fee391", "#fec44f", "#fe9929", "#ec7014", "#cc4c02", "#8c2d04"].slice().reverse(),
            // Colorbrewer YlOrBr-7
            //colors: ["#ffffd4", "#fee391", "#fec44f", "#fe9929", "#ec7014", "#cc4c02", "#8c2d04"],
            endpoint_type: legend_endpoints.out_of_range,
            decimal_places: 0,
        },
        intensity_change: {
            edges: [0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5],
            colors: ["#ffffe5", "#fff7bc", "#fee391", "#fec44f", "#fe9929", "#ec7014", "#cc4c02", "#8c2d04"],
            endpoint_type: legend_endpoints.lower_in_range,
            decimal_places: 1,
        },
        return_time: {
            edges: [0, 10, 25, 50, 100, 200],
            // Colorbrewer YlOrBr-7
            //colors: ["#ffffd4", "#fee391", "#fec44f", "#fe9929", "#ec7014", "#cc4c02", "#8c2d04"],
            // Colorbrewer YlOrBr-6
            colors: ["#ffffd4", "#fee391", "#fec44f", "#fe9929", "#d95f0e", "#993404" ].slice().reverse(),
            endpoint_type: legend_endpoints.lower_in_range,
            decimal_places: 0,
        },
        frequency_change: {
            edges: [1.0, 2.0, 3.0, 4.0, 5.0, 6.0],
            // Colorbrewer YlOrBr-7
            //colors: ["#ffffd4", "#fee391", "#fec44f", "#fe9929", "#ec7014", "#cc4c02", "#8c2d04"],
            // Colorbrewer YlOrBr-6
            colors: ["#ffffd4", "#fee391", "#fec44f", "#fe9929", "#d95f0e", "#993404" ],
            endpoint_type: legend_endpoints.lower_in_range,
            decimal_places: 0,
        },
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
            "#covariate2Group": false,
        },
        intensity_change: {
            "#covariateGroup": true,
            "#calculationGroup": true,
            "#tauReturnGroup": true,
            "#intensityGroup": false,
            "#covariate2Group": true,
        },
        return_time: {
            "#covariateGroup": true,
            "#calculationGroup": true,
            "#tauReturnGroup": false,
            "#intensityGroup": true,
            "#covariate2Group": false,
        },
        frequency_change: {
            "#covariateGroup": true,
            "#calculationGroup": true,
            "#tauReturnGroup": false,
            "#intensityGroup": true,
            "#covariate2Group": true,
        },
    }
};

const ui_map = new UIMap('map', tilelayerurl);



/// Helper function to request data points from a URL. 
async function fetch_data(url) {
    let response = await fetch(url);
    let data = await response.json();
    return data;
}

async function update_data_layer(url, colorbar) {
    ui_map.hide_overlay();
    const data = await fetch_data(url);
    ui_map.update_data_layer(data, colorbar);
}

async function update_boundary_layer(layer_name) {
    const valid_layers = {
        'local_authorities': (feature) => feature.values_.local_authority.replaceAll(' ', '\n'),
        //'police': (feature) => "hi",
        'fire_rescue': (feature) => feature.values_.sfrlsoname.replaceAll(',', ',\n').replaceAll(' and ', ' and\n'),
        'health_boards': (feature) => feature.values_.HBName.replaceAll(' ', '\n'),
        'health_integration_authorities': (feature) => feature.values_.HIAName.replaceAll(' ', '\n'),
    };

    if (!(layer_name in valid_layers)) {
        ui_map.hide_boundary_layer();
        return;
    }

    const url = new URL(
        window.location.protocol + "//" + window.location.host + "/" +
        window.location.pathname + "/boundaries/" + layer_name
    ); 
    const data = await fetch_data(url.href);
    ui_map.update_boundary_layer(data, valid_layers[layer_name]);
}

function update_ui(slider_values) {
    
    const scenario = $("#scenario")[0].value;
    const next_choice = $(selection_tree[scenario].next_choice)[0].value;

    // Update slider visibility
    for (let ui_item_id in selection_tree[scenario][next_choice]) {
        const ui_item = $(ui_item_id)[0];
        const ui_item_is_visible = selection_tree[scenario][next_choice][ui_item_id];
        ui_item.style.display = ui_item_is_visible ? "block" : "none";
    }

    // Enforce Covariate 1/2 value constraints
    const calculation = $("#calculation")[0].value;
    const covariate_max = parseFloat($('#covariateParam')[0].max);
    const covariate_step = parseFloat($('#covariateParam')[0].step);
    if ((calculation.search('_change') > 0) && (slider_values['#covariateParam'] >= covariate_max - covariate_step)) {
        $('#covariateParam')[0].value = covariate_max - covariate_step;
    }
    if (slider_values['#covariate2Param'] <= slider_values["#covariateParam"] + covariate_step) {
        $('#covariate2Param')[0].value = slider_values["#covariateParam"] + covariate_step;
    }

    // Show selected tick with a special class.
    const slider_ticks_pairs = [
        ["#covariateParam", "#covariateTicks", 1],
        ["#covariate2Param", "#covariate2Ticks", 1],
        ["#tauReturnParam", "#tauReturnTicks", 0],
        ["#intensityParam", "#intensityTicks", 0],
    ];
    for (const [slider_id, tick_collection, decimal_places] of slider_ticks_pairs) {
        const slider_txt = slider_values[slider_id].toFixed(decimal_places);
        for (var tick of $(tick_collection)[0].children) {
            tick.classList = (tick.innerHTML === slider_txt)
                ? "ticks-txt ticks-on"
                : "ticks-txt";
        }
    }

    // Update links for downloading datasets.
    $('#download_netcdf').prop({
        'href': make_data_url(slider_values) + '/netcdf',
    });
    $('#download_csv').prop({
        'href': make_data_url(slider_values) + '/csv',
    });
    return colorbar[scenario][next_choice] // FIXME
}

function make_data_url(slider_values) {
    const scenario = $("#scenario")[0].value;
    var url_endpoint = new URL(
        window.location.protocol + "//" + window.location.host + "/" +
        window.location.pathname + "/data/" + scenario
    ); 

    if (scenario == "extreme_temp") {

        const calculation = $("#calculation")[0].value;

        url_endpoint.pathname += '/' + calculation;
        url_endpoint.pathname += '/' + slider_values["#covariateParam"];
        if (calculation == "intensity") {
            url_endpoint.pathname += '/' + slider_values["#tauReturnParam"];
        }
        else if(calculation == "intensity_change") {
            url_endpoint.pathname += '/' + slider_values["#tauReturnParam"] + '/' + slider_values["#covariate2Param"];
        }
        else if(calculation == "return_time") {
            url_endpoint.pathname += '/' + slider_values["#intensityParam"];
        }
        else if(calculation == "frequency_change") {
            url_endpoint.pathname += '/' + slider_values["#intensityParam"] + '/' + slider_values["#covariate2Param"];
        }
    }
    return url_endpoint.href;

}

function get_slider_values() {
    var result = new Object();
    const slider_ids = [
        "#covariateParam",
        "#covariate2Param",
        "#tauReturnParam",
        "#intensityParam",
    ];

    for (const id of slider_ids) {
        result[id] = parseFloat($(id).val());
    }

    const calculation = $("#calculation")[0].value;
    const covariate_max = parseFloat($('#covariateParam')[0].max);
    const covariate_step = parseFloat($('#covariateParam')[0].step);

    // Ensure covariate < 4.0 if comparing different scenarios
    if (calculation.search('_change') > 0 && result['#covariateParam'] >= covariate_max - covariate_step) {
        result["#covariateParam"] = covariate_max - covariate_step;
    }

    // Ensure covariate1 < covariate2
    if (result['#covariate2Param'] <= result["#covariateParam"] + covariate_step) {
        result['#covariate2Param'] = result["#covariateParam"] + covariate_step;
    }
    return result;
}

var previous_slider_values = {};
async function on_user_input() {
    /// Handler for UI events
    const slider_values = get_slider_values();
    const colorbar = update_ui(slider_values);

    // Early exit if nothing changed.
    if (JSON.stringify(previous_slider_values) === JSON.stringify(slider_values))
        return;
    previous_slider_values = slider_values;

    const url_endpoint = make_data_url(slider_values);
    await update_data_layer(url_endpoint, colorbar);
    draw_legend(colorbar.edges, colorbar.colors, colorbar.endpoint_type, colorbar.decimal_places);
}

check_disclaimer_cookie();

$("#covariateParamLabel")[0].value = "Covariate: <span style=\"font-weight:bold\">1.5</span>"; 
$("#covariateParam")[0].oninput = on_user_input;
$("#covariate2ParamLabel")[0].value = "Covariate 2: <span style=\"font-weight:bold\">1.5</span>"; 
$("#covariate2Param")[0].oninput = on_user_input;
$("#tauReturnParamLabel")[0].value = "Covariate: <span style=\"font-weight:bold\">100</span>"; 
$("#tauReturnParam")[0].oninput = on_user_input;
$("#intensityParamLabel")[0].value = "Intensity: <span style=\"font-weight:bold\">100</span>"; 
$("#intensityParam")[0].oninput = on_user_input;

$("#scenario")[0].oninput = on_user_input; 
$("#calculation")[0].oninput = on_user_input; 

var opacityInput = $("#opacityInput")[0];
opacityInput.value = 1.0;
opacityInput.oninput = function() {
    const opacity = parseFloat(opacityInput.value);
    ui_map.set_data_layer_opacity(opacity);
}

var boundaryInput = $("#boundaryLayer")[0];
boundaryInput.oninput = async function() {
    const boundary_layer = boundaryInput.value;
    await update_boundary_layer(boundary_layer);
}

on_user_input();

boundaryInput.value = "none"
await update_boundary_layer("none");

    // Update the legend label's units
    var legend_label = $("#legend-label")[0];
    console.log(legend_label);
    if (calculation == "intensity") {
        legend_label.innerHTML = "Legend (in °C):";
    }
    else if (calculation == "return_time") {
        legend_label.innerHTML = "Legend (in years):";
    }
    else {
        legend_label.innerHTML = "Legend:";
    }

