import $ from 'jquery';
import Cookies from "js-cookie";

import {apply_color_map, legend_endpoints} from "../src/color_map.js";
import {draw_legend} from "../src/legend.js";
import {UIMap} from "../src/map.js";
import {make_slider} from "../src/slider.js";
import {attach_postcode_search} from "../src/postcode_search.js"

function check_disclaimer_cookie() {
    /// Redirects to the disclaimer page if the ToS have not been accepted.
    if (!Cookies.get('accepted_tos')) {
        window.location.replace(window.location.href + '/disclaimer');
    }
}

var previous_input_values = {};
var hazard_metadata = {};
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
    $("#opacityInput")[0].oninput();
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

function update_ui(input_values) {
    
    const scenario = input_values["#scenario"];
    const calculation = input_values["#calculation"];

    // Enforce Covariate 1 and 2 value constraints
    const covariate_min = parseFloat($('#param_covariate')[0].min);
    const covariate_step = parseFloat($('#param_covariate')[0].step);
    if ((calculation.search('_change') > 0) && (input_values['#param_covariate'] == covariate_min)) {
        $('#param_covariate')[0].value = covariate_min + covariate_step;
    }
    if (input_values['#param_covariate_comp'] >= input_values["#param_covariate"] - covariate_step) {
        $('#param_covariate_comp')[0].value = input_values["#param_covariate"] - covariate_step;
    }

    // Update links for downloading datasets.
    $('#download_netcdf').prop({
        'href': make_data_url(input_values, 'netcdf'),
    });
    $('#download_csv').prop({
        'href': make_data_url(input_values, 'csv'),
    });

    let hazard_meta = get_hazard_function_meta(scenario, calculation);
    var calculation_description_text = hazard_meta["calculation_description_template"];
    for (const arg_name of hazard_meta["arg_names"]) {
        const arg_value = $("#param_" + arg_name)[0].value;
        calculation_description_text = calculation_description_text.replaceAll("{" + arg_name + "}", arg_value);
    }
    var calculation_description = $('#calculation_description')[0];
    calculation_description.innerHTML = calculation_description_text;
}

function make_data_url(input_values, format) {
    const scenario = input_values["#scenario"];
    const calculation = input_values["#calculation"];

    var url_endpoint = new URL(
        window.location.protocol + "//" + window.location.host + 
        window.location.pathname + "/data/map/" + scenario + "_" + calculation
        + (format ? "/" + format : "")
    ); 

    let hazard_meta = get_hazard_function_meta(scenario, calculation);
    for (const arg_name of hazard_meta["arg_names"]) {
        const arg_value = input_values["#param_" + arg_name];
        url_endpoint.searchParams.append(arg_name, arg_value);
    }

    return url_endpoint.href;
}

/// Get the values of the input elements in the UI
function get_input_values() {
    var result = new Object();

    const dropdown_ids = [
        "#scenario",
        "#calculation",
    ];
    for (const id of dropdown_ids) {
        result[id] = $(id)[0].value;
    }

    // Get hazard specific inputs
    const scenario = result["#scenario"];
    const calculation = result["#calculation"];
    let hazard_meta = get_hazard_function_meta(scenario, calculation);
    for (const arg_name of hazard_meta["arg_names"]) {
        const input_id = "#param_" + arg_name;
        const input_value = $(input_id)[0].value;
        result[input_id] = input_value;
    }

    const covariate_min = parseFloat($('#param_covariate')[0].min);
    const covariate_step = parseFloat($('#param_covariate')[0].step);

    // Ensure covariate < 4.0 if comparing different scenarios
    if (calculation.search('_change') > 0 && result['#param_covariate'] == covariate_min) {
        result["#param_covariate"] = covariate_min + covariate_step;
    }

    // Ensure covariate1 > covariate2
    if (result['#param_covariate_comp'] >= result["#param_covariate"] - covariate_step) {
        result['#param_covariate_comp'] = result["#param_covariate"] - covariate_step;
    }
    return result;
}

async function on_user_input() {
    /// Handler for UI events
    const input_values = get_input_values();
    update_ui(input_values);

    // Early exit if nothing changed.
    if (JSON.stringify(previous_input_values) === JSON.stringify(input_values))
        return;
    previous_input_values = input_values;

    const url_endpoint = make_data_url(input_values, '');
    const colorbar = get_hazard_function_meta(input_values["#scenario"], input_values["#calculation"]).legend;
    await update_data_layer(url_endpoint, colorbar);
}


function update_legend() {
    let scenario = $("#scenario")[0].value;
    let calculation = $("#calculation")[0].value;
    let hazard_meta = get_hazard_function_meta(scenario, calculation);

    const legend = hazard_meta.legend;
    draw_legend(legend.edges, legend.colors, legend.endpoint_type, legend.decimal_places);

    const legend_label = $("#legend-label")[0];
    legend_label.innerText = legend.label;
}

// --- Initialize the user interface

/// Populate hazard_metadata with data from the server.
async function get_hazard_metadata() {
    const url = new URL(
        window.location.protocol + "//" + window.location.host + "/" +
        window.location.pathname + "/data/metadata"
    ); 
    let response = await fetch(url);
    hazard_metadata = await response.json();
}

function get_hazard_function_meta(scenario, calculation) {
    let hazard = hazard_metadata["ui_selection"][scenario]["calculations"][calculation];
    return hazard_metadata["hazards"][hazard];
}

function on_calculation_change() {
    let scenario = $("#scenario")[0].value;
    let calculation = $("#calculation")[0].value;
    let hazard_meta = get_hazard_function_meta(scenario, calculation);

    // Update comparitave covariate visibility
    let covariate_comp = $("#covariate2Group")[0];
    covariate_comp.style.display = hazard_meta["arg_names"].some(e => e === "covariate_comp") ? "block" : "none";

    // Create sliders for other arguments.
    $("#sliderGroup")[0].textContent = "";

    let arg_meta = hazard_meta["arg_names"].map(function(a, i) { return [a, hazard_meta["args"][i], hazard_meta["arg_labels"][i]]; });
    for (const [arg_name, arg_range, arg_label] of arg_meta) {
        if (arg_label == '')
            continue;
        make_slider({
            range_id: "param_" + arg_name,
            values: arg_range,
            label: arg_label,
            root_div_id: "sliderGroup",
            on_user_input: on_user_input,
        });
    }

    on_user_input();
    update_legend();
}

function update_calculation_options() {
    let scenario_selector = $("#scenario")[0];
    let calculation_selector = $("#calculation")[0];
    let scenario = scenario_selector.value;
    for (var calculation_option of calculation_selector.options) {
        const calculation_id = calculation_option.value;
        let hazard = hazard_metadata["ui_selection"][scenario]["calculations"][calculation_id];
        let label_text = hazard_metadata["hazards"][hazard]["calculation_dropdown_label"];
        calculation_option.innerText = label_text;
    }
    on_calculation_change();
}

function on_scenario_change() {
    // Update calculation dropdown options
    update_calculation_options();
    // Update datalayer
    on_user_input();
    update_legend();
}

/// Update 
async function init_ui() {
    check_disclaimer_cookie();

    await get_hazard_metadata();

    let scenario_selector = $("#scenario")[0];
    scenario_selector.oninput = on_scenario_change;

    $("#param_covariate")[0].oninput = on_user_input;
    $("#param_covariate_comp")[0].oninput = on_user_input;

    for (const scenario in hazard_metadata["ui_selection"]) {
        const option = document.createElement("option");
        const hazard_label_text = hazard_metadata["ui_selection"][scenario]["ui_label"];
        const hazard_label = document.createTextNode(hazard_label_text);
        option.setAttribute("value", scenario);
        option.appendChild(hazard_label);
        scenario_selector.appendChild(option);
    }
    // Update calculation dropdown options -- set the supported hazards
    update_calculation_options();

    // Set what happens when the calculation is changed.
    let calculation_selector = $("#calculation")[0];
    calculation_selector.oninput = on_calculation_change;

    var opacityInput = $("#opacityInput")[0];
    opacityInput.value = 0.8; // Set default opacity
    opacityInput.oninput = function() {
        const opacity = parseFloat(opacityInput.value);
        ui_map.set_data_layer_opacity(opacity);
    }

    var boundaryInput = $("#boundaryLayer")[0];
    boundaryInput.oninput = async function() {
        const boundary_layer = boundaryInput.value;
        await update_boundary_layer(boundary_layer);
    }

    boundaryInput.value = "none"
    await update_boundary_layer("none");

    // Setup the Postcode search feature
    let postcode_search_button = $("#button-search-postcode")[0];
    let postcode_search_input = $("#search-postcode")[0];
    attach_postcode_search(
        postcode_search_button, 
        postcode_search_input,
        (coordinate) => { ui_map.select_feature_at(coordinate); },
    );
}

await init_ui();
