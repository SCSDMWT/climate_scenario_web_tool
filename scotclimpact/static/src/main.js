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
    },
    sustained_3day_Tmin: {
        intensity: {
            edges: [14, 15, 16, 17, 18, 19, 20, 21],
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
    },
    extreme_1day_precip: {
        intensity: {
            edges: [50, 75, 100, 125, 150],
            // Colorbrewer PuBu-6
            colors: ['#f1eef6', '#d0d1e6', '#a6bddb', '#74a9cf', '#2b8cbe', '#045a8d'],
            endpoint_type: legend_endpoints.out_of_range,
            decimal_places: 0,
        },
        intensity_change: {
            edges: [0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5],
            // Colorbrewer PuBu-8
            colors: ["#fff7fb", "#ece7f2", "#d0d1e6", "#a6bddb", "#74a9cf", "#3690c0", "#0570b0", "#034e7b"],
            endpoint_type: legend_endpoints.lower_in_range,
            decimal_places: 1,
        },
        return_time: {
            edges: [0, 10, 25, 50, 100, 200],
            // Colorbrewer PuBu-6
            colors: ["#f1eef6", "#d0d1e6", "#a6bddb", "#74a9cf", "#2b8cbe", "#045a8d"].slice().reverse(),
            endpoint_type: legend_endpoints.lower_in_range,
            decimal_places: 0,
        },
        frequency_change: {
            edges: [1.0, 2.0, 3.0, 4.0, 5.0, 6.0],
            // Colorbrewer PuBu-6
            colors: ["#f1eef6", "#d0d1e6", "#a6bddb", "#74a9cf", "#2b8cbe", "#045a8d"],
            endpoint_type: legend_endpoints.lower_in_range,
            decimal_places: 0,
        },
    },
    extreme_3day_precip: {
        intensity: {
            edges: [50, 75, 100, 125, 150],
            // Colorbrewer PuBu-6
            colors: ['#f1eef6', '#d0d1e6', '#a6bddb', '#74a9cf', '#2b8cbe', '#045a8d'],
            endpoint_type: legend_endpoints.out_of_range,
            decimal_places: 0,
        },
        intensity_change: {
            edges: [0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5],
            // Colorbrewer PuBu-8
            colors: ["#fff7fb", "#ece7f2", "#d0d1e6", "#a6bddb", "#74a9cf", "#3690c0", "#0570b0", "#034e7b"],
            endpoint_type: legend_endpoints.lower_in_range,
            decimal_places: 1,
        },
        return_time: {
            edges: [0, 10, 25, 50, 100, 200],
            // Colorbrewer PuBu-6
            colors: ["#f1eef6", "#d0d1e6", "#a6bddb", "#74a9cf", "#2b8cbe", "#045a8d"].slice().reverse(),
            endpoint_type: legend_endpoints.lower_in_range,
            decimal_places: 0,
        },
        frequency_change: {
            edges: [1.0, 2.0, 3.0, 4.0, 5.0, 6.0],
            // Colorbrewer PuBu-6
            colors: ["#f1eef6", "#d0d1e6", "#a6bddb", "#74a9cf", "#2b8cbe", "#045a8d"],
            endpoint_type: legend_endpoints.lower_in_range,
            decimal_places: 0,
        },
    },
};

const selection_tree = {
    extreme_temp: {
        next_choice: "#calculation",
        intensity: {
            "#covariateGroup": true,
            "#calculationGroup": true,
            "#tauReturnGroup": true,
            "#intensityGroup_C": false,
            "#intensityGroup_mm": false,
            "#covariate2Group": false,
        },
        intensity_change: {
            "#covariateGroup": true,
            "#calculationGroup": true,
            "#tauReturnGroup": true,
            "#intensityGroup_C": false,
            "#intensityGroup_mm": false,
            "#covariate2Group": true,
        },
        return_time: {
            "#covariateGroup": true,
            "#calculationGroup": true,
            "#tauReturnGroup": false,
            "#intensityGroup_C": true,
            "#intensityGroup_mm": false,
            "#covariate2Group": false,
        },
        frequency_change: {
            "#covariateGroup": true,
            "#calculationGroup": true,
            "#tauReturnGroup": false,
            "#intensityGroup_C": true,
            "#intensityGroup_mm": false,
            "#covariate2Group": true,
        },
    },
    sustained_3day_Tmin: {
        next_choice: "#calculation",
        intensity: {
            "#covariateGroup": true,
            "#calculationGroup": true,
            "#tauReturnGroup": true,
            "#intensityGroup_C": false,
            "#intensityGroup_mm": false,
            "#covariate2Group": false,
        },
        intensity_change: {
            "#covariateGroup": true,
            "#calculationGroup": true,
            "#tauReturnGroup": true,
            "#intensityGroup_C": false,
            "#intensityGroup_mm": false,
            "#covariate2Group": true,
        },
        return_time: {
            "#covariateGroup": true,
            "#calculationGroup": true,
            "#tauReturnGroup": false,
            "#intensityGroup_C": true,
            "#intensityGroup_mm": false,
            "#covariate2Group": false,
        },
        frequency_change: {
            "#covariateGroup": true,
            "#calculationGroup": true,
            "#tauReturnGroup": false,
            "#intensityGroup_C": true,
            "#intensityGroup_mm": false,
            "#covariate2Group": true,
        },
    },
    extreme_1day_precip: {
        next_choice: "#calculation",
        intensity: {
            "#covariateGroup": true,
            "#calculationGroup": true,
            "#tauReturnGroup": true,
            "#intensityGroup_C": false,
            "#intensityGroup_mm": false,
            "#covariate2Group": false,
        },
        intensity_change: {
            "#covariateGroup": true,
            "#calculationGroup": true,
            "#tauReturnGroup": true,
            "#intensityGroup_C": false,
            "#intensityGroup_mm": false,
            "#covariate2Group": true,
        },
        return_time: {
            "#covariateGroup": true,
            "#calculationGroup": true,
            "#tauReturnGroup": false,
            "#intensityGroup_C": false,
            "#intensityGroup_mm": true,
            "#covariate2Group": false,
        },
        frequency_change: {
            "#covariateGroup": true,
            "#calculationGroup": true,
            "#tauReturnGroup": false,
            "#intensityGroup_C": false,
            "#intensityGroup_mm": true,
            "#covariate2Group": true,
        },
    },
    extreme_3day_precip: {
        next_choice: "#calculation",
        intensity: {
            "#covariateGroup": true,
            "#calculationGroup": true,
            "#tauReturnGroup": true,
            "#intensityGroup_C": false,
            "#intensityGroup_mm": false,
            "#covariate2Group": false,
        },
        intensity_change: {
            "#covariateGroup": true,
            "#calculationGroup": true,
            "#tauReturnGroup": true,
            "#intensityGroup_C": false,
            "#intensityGroup_mm": false,
            "#covariate2Group": true,
        },
        return_time: {
            "#covariateGroup": true,
            "#calculationGroup": true,
            "#tauReturnGroup": false,
            "#intensityGroup_C": false,
            "#intensityGroup_mm": true,
            "#covariate2Group": false,
        },
        frequency_change: {
            "#covariateGroup": true,
            "#calculationGroup": true,
            "#tauReturnGroup": false,
            "#intensityGroup_C": false,
            "#intensityGroup_mm": true,
            "#covariate2Group": true,
        },
    },
};

const calculation_dropdown_labels = {
    "#calculation_intensity": "HAZARD expected to be exceeded in # years",
    "#calculation_intensity_change": "Change in HAZARD expected in # years",
    "#calculation_return_time": "Expected return time of HAZARD",
    "#calculation_return_time_change": "Change in frequency of HAZARD",
}
const intensity_label_ids = {
    "extreme_temp": "#intensityParamLabel_C",
    "sustained_3day_Tmin": "#intensityParamLabel_C",
    "extreme_1day_precip": "#intensityParamLabel_mm",
    "extreme_3day_precip": "#intensityParamLabel_mm",
}
const intensity_labels = {
    "extreme_temp": "Hottest temperature (in °C)",
    "sustained_3day_Tmin": "Highest sustained heat (in °C)",
    "extreme_1day_precip": "Highest 1-day rainfall (in mm)",
    "extreme_1day_precip": "Highest 3-day rainfall (in mm)",
}
const calculation_descriptions = {
    "intensity": "<p>Intensity shows the HAZARD that is expected to be seen in Z_RETURN_TIME years at a global temperature anomaly of +X_COV °C compared to the pre-industrial average.</p>",
    "intensity_change": "<p>Change in Intensity shows the change in the HAZARD that is expected to be seen in Z_RETURN_TIME years at a global temperature anomaly of +Y_COV °C compared to a global temperature anomaly of +X_COV °C.</p>",
    "return_time": "<p>Return Time shows the number of years in which a HAZARD of Z_INTENSITY INTENSITY_UNIT is expected to be exceeded at least once at a global temperature anomaly of +X_COV °C compared to the pre-industrial average.</p>",
    "frequency_change": "<p>Change in Frequency shows how many times more frequent a HAZARD of Z_INTENSITY INTENSITY_UNIT is expected to be seen at a global temperature anomaly of +Y_COV °C compared to a global temperature anomaly +X_COV °C.</p>",
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

function update_ui(input_values) {
    
    const scenario = input_values["#scenario"];
    const next_choice = $(selection_tree[scenario].next_choice)[0].value;

    // Update slider visibility
    for (let ui_item_id in selection_tree[scenario][next_choice]) {
        const ui_item = $(ui_item_id)[0];
        const ui_item_is_visible = selection_tree[scenario][next_choice][ui_item_id];
        ui_item.style.display = ui_item_is_visible ? "block" : "none";
    }

    // Enforce Covariate 1/2 value constraints
    const calculation = input_values["#calculation"];
    const covariate_max = parseFloat($('#covariateParam')[0].max);
    const covariate_step = parseFloat($('#covariateParam')[0].step);
    if ((calculation.search('_change') > 0) && (input_values['#covariateParam'] >= covariate_max - covariate_step)) {
        $('#covariateParam')[0].value = covariate_max - covariate_step;
    }
    if (input_values['#covariate2Param'] <= input_values["#covariateParam"] + covariate_step) {
        $('#covariate2Param')[0].value = input_values["#covariateParam"] + covariate_step;
    }

    // Show selected tick with a special class.
    const slider_ticks_pairs = [
        ["#covariateParam", "#covariateTicks", 1],
        ["#covariate2Param", "#covariate2Ticks", 1],
        ["#tauReturnParam", "#tauReturnTicks", 0],
        ["#intensityParam_C", "#intensityTicks_C", 0],
        ["#intensityParam_mm", "#intensityTicks_mm", 0],
    ];
    for (const [slider_id, tick_collection, decimal_places] of slider_ticks_pairs) {
        const slider_txt = input_values[slider_id].toFixed(decimal_places);
        for (var tick of $(tick_collection)[0].children) {
            tick.classList = (tick.innerHTML === slider_txt)
                ? "ticks-txt ticks-on"
                : "ticks-txt";
        }
    }

    // Update links for downloading datasets.
    $('#download_netcdf').prop({
        'href': make_data_url(input_values, 'netcdf'),
    });
    $('#download_csv').prop({
        'href': make_data_url(input_values, 'csv'),
    });

    // Update the legend label's units
    var legend_label = $("#legend-label")[0];
    if (calculation == "intensity" && (scenario == "extreme_temp" || scenario == "sustained_3day_Tmin")) {
        legend_label.innerHTML = "Legend (in °C):";
    }
    else if (calculation == "intensity" && (scenario == "extreme_1day_precip")) {
        legend_label.innerHTML = "Legend (in mm):";
    }
    else if (calculation == "return_time") {
        legend_label.innerHTML = "Legend (in years):";
    }
    else {
        legend_label.innerHTML = "Legend:";
    }



    var calculation_description = $('#calculation_description')[0];
    var intensity_value, intensity_unit, hazard_name;
    if (scenario == "extreme_temp") {
        intensity_value = input_values["#intensityParam_C"];
        intensity_unit = "°C";
        hazard_name = "hottest temperature";
    }
    if (scenario == "sustained_3day_Tmin") {
        intensity_value = input_values["#intensityParam_C"];
        intensity_unit = "°C";
        hazard_name = "highest 3-day sustained heat";
    }
    if (scenario == "extreme_1day_precip"){
        intensity_value = input_values["#intensityParam_mm"];
        intensity_unit = "mm";
        hazard_name = "1-day rainfall";
    }
    if (scenario == "extreme_3day_precip"){
        intensity_value = input_values["#intensityParam_mm"];
        intensity_unit = "mm";
        hazard_name = "3-day rainfall";
    }
    // Calculation dropdown values
    const calculation_dropdown_items = [
        "#calculation_intensity",
        "#calculation_intensity_change",
        "#calculation_return_time",
        "#calculation_return_time_change",
    ];
    for (const item_id of calculation_dropdown_items) {
        var item = $(item_id)[0];
        const label = calculation_dropdown_labels[item_id].replaceAll("HAZARD", hazard_name);
        item.innerHTML = label.charAt(0).toUpperCase() + label.slice(1);
    }
    // Intensity labels
    const intensity_label_id = intensity_label_ids[scenario];
    const intensity_label = $(intensity_label_id)[0];
    intensity_label.innerHTML = intensity_labels[scenario];
    // Insert slider values in the calculation description box
    calculation_description.innerHTML = 
        calculation_descriptions[calculation]
            .replaceAll("X_COV", input_values["#covariateParam"])
            .replaceAll("Y_COV", input_values["#covariate2Param"])
            .replaceAll("Z_RETURN_TIME", input_values["#tauReturnParam"])
            .replaceAll("HAZARD", hazard_name)
            .replaceAll("INTENSITY_UNIT", intensity_unit)
            .replaceAll("Z_INTENSITY", intensity_value);


    return colorbar[scenario][next_choice] // FIXME
}

function make_data_url(input_values, format) {
    const scenario = input_values["#scenario"];
    const calculation = input_values["#calculation"];

    var url_endpoint = new URL(
        window.location.protocol + "//" + window.location.host + 
        window.location.pathname + "/data/map/" + scenario+ "_" + calculation
        + (format ? "/" + format : "")
    ); 


    url_endpoint.searchParams.append('covariate', input_values["#covariateParam"]);

    if (calculation == "intensity") {
        url_endpoint.searchParams.append('return_time', input_values["#tauReturnParam"]);
    }
    if(calculation == "intensity_change") {
        url_endpoint.searchParams.append('return_time', input_values["#tauReturnParam"]);
        url_endpoint.searchParams.append('covariate_comp', input_values["#covariate2Param"]);
    }

    if (scenario == "extreme_temp" || scenario == "sustained_3day_Tmin") {
        if(calculation == "return_time") {
            url_endpoint.searchParams.append('intensity', input_values["#intensityParam_C"]);
        }
        if(calculation == "frequency_change") {
            url_endpoint.searchParams.append('intensity', input_values["#intensityParam_C"]);
            url_endpoint.searchParams.append('covariate_comp', input_values["#covariate2Param"]);
        }
    }
    if (scenario == "extreme_1day_precip" || scenario == "extreme_3day_precip") {
        if(calculation == "return_time") {
            url_endpoint.searchParams.append('intensity', input_values["#intensityParam_mm"]);
        }
        if(calculation == "frequency_change") {
            url_endpoint.searchParams.append('intensity', input_values["#intensityParam_mm"]);
            url_endpoint.searchParams.append('covariate_comp', input_values["#covariate2Param"]);
        }
    }
    return url_endpoint.href;

}

/// Get the values of the input elements in the UI
function get_input_values() {
    var result = new Object();
    const slider_ids = [
        "#covariateParam",
        "#covariate2Param",
        "#tauReturnParam",
        "#intensityParam_C",
        "#intensityParam_mm",
    ];
    const dropdown_ids = [
        "#scenario",
        "#calculation",
    ];

    for (const id of slider_ids) {
        result[id] = parseFloat($(id).val());
    }
    for (const id of dropdown_ids) {
        result[id] = $(id)[0].value;
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

var previous_input_values = {};
async function on_user_input() {
    /// Handler for UI events
    const input_values = get_input_values();
    const colorbar = update_ui(input_values);

    // Early exit if nothing changed.
    if (JSON.stringify(previous_input_values) === JSON.stringify(input_values))
        return;
    previous_input_values = input_values;

    const url_endpoint = make_data_url(input_values, '');
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
$("#intensityParamLabel_C")[0].value = "Intensity: <span style=\"font-weight:bold\">100</span>"; 
$("#intensityParam_C")[0].oninput = on_user_input;

//$("#intensityParamLabel_mm")[0].value = "Intensity: <span style=\"font-weight:bold\">100</span>"; 
$("#intensityParam_mm")[0].oninput = on_user_input;

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
