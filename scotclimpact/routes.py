from collections import namedtuple
from functools import partial
import io
import json
import markdown
import os

from flask import current_app as app
from flask import render_template, request, make_response, send_file

from . import db
from .developing_process import (
    init_composite_fit,
)
from .data_helpers import xarray_to_geojson, is_number, validate_args, str_lower
from .boundary_layer import is_valid_boundary_layer, get_boundary_layer
from .cache import get_cache
from .hazards import (ui_selection, hazards)

def menu_items():
    '''Returns a list of named tuples describing the items in the navigation menu'''
    MenuItem = namedtuple("MenuItem", "title path order")
    return [
        MenuItem("Disclaimer", "disclaimer", 2),
    ]

@app.route('/')
@get_cache().cached(timeout=50)
def index():
    return render_template(
        'map.html',
        navigation=menu_items(),
        mapserverurl=app.config['MAPSERVER_URL'],
        tilelayerurl=app.config['TILE_LAYER_URL'],
    )

@app.route('/disclaimer')
@get_cache().cached(timeout=50)
def disclaimer():
    with open("scotclimpact/pages/disclaimer.md", "r") as f:
        disclaimer_text = markdown.markdown(f.read())

    return render_template(
        'disclaimer.html',
        disclaimer_text=disclaimer_text,
        navigation=menu_items(),
    )

def make_json_response(json_data):
    '''Serialize JSON and create a response object'''
    json_str = json.dumps(json_data)

    response = make_response(send_file(
        io.BytesIO(json_str.encode('utf-8')), 
        mimetype='application/json'
    ))
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response


def make_download_name(endpoint_name, params, ext):
    filename_base = endpoint_name.replace("/", "_")
    params_list = "_".join([str(param) for param in params])
    return f"{filename_base}_{params_list}.{ext}"

def make_netcdf_response(dataset, endpoint_name, params):
    '''Return an xarray dataset as NetCDF file'''
    download_name = make_download_name(endpoint_name, params, 'nc')

    file_bytes = dataset.to_netcdf()
    return send_file(
        io.BytesIO(file_bytes),
        download_name=download_name
    )

def make_csv_response(dataset, endpoint_name, params):
    '''Return an xarray dataset as a CSV file'''
    download_name = make_download_name(endpoint_name, params, 'csv')
    file_content = dataset.to_dataframe().reset_index().to_csv(index=False)
    return send_file(
        io.BytesIO(file_content.encode('utf-8')),
        download_name=download_name,
    )


SUPPORTED_FORMATS = ['geojson', 'netcdf', 'csv']

def is_supported_format(fmt):
    '''Predicate to check if fmt is a supported data format'''
    return fmt.lower() in SUPPORTED_FORMATS

def make_data_response(dataset, format, endpoint_name, params, ci_report_url):
    # Make the response object
    if format == 'geojson':
        json_data = xarray_to_geojson(endpoint_name, dataset, ci_report_url=ci_report_url)
        return make_json_response(json_data)
    if format == 'netcdf':
        return make_netcdf_response(dataset, endpoint_name, params)
    if format == 'csv':
        return make_csv_response(dataset, endpoint_name, params)


@app.route('/boundaries/<layer_name>')
@get_cache().cached(timeout=50)
@validate_args(('layer_name', is_valid_boundary_layer, str))
def bondaries_local_authorities(layer_name):
    return get_boundary_layer(layer_name)


def parse_and_validate_args(hazard):
    '''Get hazard function arguments from the query string convert them to the correct type and
    make sure the values are valid'''
    args = [
        request.args.get(arg_name, '')
        for arg_name 
        in hazard['arg_names']
    ]
    for i, arg in enumerate(args):
        arg_name = hazard['arg_names'][i]
        if not is_number(arg):
            return []
        args[i] = arg = hazard['arg_types'][arg_name](arg)
        if not arg in hazard['args'][i]:
            return []
    return args


@app.route('/data/metadata')
def get_metadata():
    """Return metadata that the client needs to draw UI elements"""
    client_keys = [
        "arg_names",
        "arg_labels",
        "calculation_dropdown_label",
        "calculation_description_template",
        "args",
        "legend",
    ]
    def trim_for_client(hazard):
        return {
            key: hazard.get(key, '')
            for key in client_keys
        }
    hazards_ = {
        hazard_name: trim_for_client(hazard)
        for hazard_name, hazard
        in hazards.items()
    }
    result = dict(ui_selection=ui_selection, hazards=hazards_)
    return make_json_response(result)


@app.route('/data/map/<function_name>')
@app.route('/data/map/<function_name>/<format>')
@get_cache().cached(timeout=60, query_string=True)
def data(function_name, format='geojson'):

    if not function_name in hazards:
        return "not found\n", 404
    if not format in {'geojson', 'csv', 'netcdf'}:
        return "Invalid arguments", 400

    hazard = hazards[function_name]

    args = parse_and_validate_args(hazard)
    if not args:
        return "Invalid arguments", 400
    if format=='geojson' and db.has_results(function=function_name, **request.args):
        return make_json_response(
            db.get_json_hazard_data(function=function_name, **request.args)
        )

    hazard_function = hazard['function']
    composite_fit = init_composite_fit(
        hazard['model_file'],
        hazard['grid_size'],
        simParams='c,loc1,scale0,scale1',
        nVariates=1000,
        preProcess=True,
    )

    result = hazard_function(composite_fit, *args)
    
    ci_report_url = partial(
            hazard['ci_report_url']
                .replace('{x}', '{x_idx}')
                .replace('{y}', '{y_idx}')
                .format,
            **request.args
    )
    return make_data_response(result, format, function_name, args, ci_report_url)


@app.route('/data/ci_report/<function_name>/<x_idx>/<y_idx>')
@get_cache().cached(timeout=60, query_string=True)
def ci_report(function_name, x_idx, y_idx):

    if not function_name in hazards:
        return "not found\n", 404

    hazard = hazards[function_name]
    args = parse_and_validate_args(hazard)
    if not args:
        return "Invalid arguments", 400

    if not is_number(x_idx) or int(x_idx) < 0 or int(x_idx) >= hazard['result_grid_size']['x']:
        return "Invalid arguments", 400
    if not is_number(y_idx) or int(y_idx) < 0 or int(y_idx) >= hazard['result_grid_size']['y']:
        return "Invalid arguments", 400
    x_idx = int(x_idx)
    y_idx = int(y_idx)
    args = args + [x_idx, y_idx]

    ci_report_function = hazard['ci_report_function']
    print(ci_report_function)
    print(args)
    composite_fit = init_composite_fit(
        hazard['model_file'],
        hazard['grid_size'],
        simParams='c,loc1,scale0,scale1',
        nVariates=1000,
        preProcess=True,
        intensityUnits=hazard.get('intensityUnits', ''),
    )

    result = ci_report_function(composite_fit, *args)
    
    return result, 200
