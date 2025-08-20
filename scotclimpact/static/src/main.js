import $ from 'jquery';

import {apply_color_map, legend_endpoints} from "../src/color_map.js";
import {draw_legend} from "../src/legend.js";
import {UIMap} from "../src/map.js";

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
        },
        return_time: {
            edges: [0, 10, 25, 50, 100, 200],
            // Colorbrewer YlOrBr-7
            //colors: ["#ffffd4", "#fee391", "#fec44f", "#fe9929", "#ec7014", "#cc4c02", "#8c2d04"],
            // Colorbrewer YlOrBr-6
            colors: ["#ffffd4", "#fee391", "#fec44f", "#fe9929", "#d95f0e", "#993404" ].slice().reverse(),
            endpoint_type: legend_endpoints.lower_in_range,
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

const ui_map = new UIMap('map', tilelayerurl);



/// Helper function to request data points from a URL. 
async function fetch_data(url) {
    let response = await fetch(url);
    let data = await response.json();
    return data;
}

async function update_data_layer(url, colorbar) {
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

    // Update slider labels
    $('#covariateParamLabel').html("Covariate: <span style=\"font-weight:bold\">" + slider_values["#covariateParam"].toFixed(1) + "</span>");
    $('#tauReturnParamLabel').html("Return time: <span style=\"font-weight:bold\">" + slider_values["#tauReturnParam"].toFixed(0) + "</span>");
    $('#intensityParamLabel').html("Intensity: <span style=\"font-weight:bold\">" + slider_values["#intensityParam"].toFixed(0) + "</span>");

    return colorbar[scenario][next_choice] // FIXME
}

function make_data_url(slider_values) {
    const scenario = $("#scenario")[0].value;
    var url_endpoint = new URL(
        window.location.protocol + "//" + window.location.host + "/" +
        window.location.pathname + "/data/" + scenario
    ); 

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

async function on_user_input() {
    /// Handler for UI events
    const slider_values = get_slider_values();
    const url_endpoint = make_data_url(slider_values)
    const colorbar = update_ui(slider_values);
    await update_data_layer(url_endpoint, colorbar);
    //draw_legend(colorbar);
    draw_legend(colorbar.edges, colorbar.colors, colorbar.endpoint_type);
}

$("#covariateParamLabel")[0].value = "Covariate: <span style=\"font-weight:bold\">1.5</span>"; 
$("#covariateParam")[0].oninput = on_user_input;
$("#tauReturnParamLabel")[0].value = "Covariate: <span style=\"font-weight:bold\">100</span>"; 
$("#tauReturnParam")[0].oninput = on_user_input;
$("#intensityParamLabel")[0].value = "Intensity: <span style=\"font-weight:bold\">100</span>"; 
$("#intensityParam")[0].oninput = on_user_input;

$("#scenario")[0].oninput = on_user_input; 
$("#calculation")[0].oninput = on_user_input; 

var opacityInput = $("#opacityInput")[0];
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
