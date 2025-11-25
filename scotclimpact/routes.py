from collections import namedtuple
import io
import json
import markdown
import os

from flask import current_app as app
from flask import render_template, request, make_response, send_file

from . import db
from .extreme_temp import (
    init_composite_fit,
    intensity_from_return_time,
    return_time_from_intensity,
    change_in_intensity,
    change_in_frequency,
    intensity_ci_report,
    return_time_ci_report,
    change_in_intensity_ci_report,
    change_in_frequency_ci_report,
)
from .data_helpers import xarray_to_geojson, is_number, validate_args, str_lower
from .boundary_layer import is_valid_boundary_layer, get_boundary_layer
from .cache import get_cache
from .hazards import hazards

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

def make_data_response(dataset, format, endpoint_name, params):
    # Make the response object
    if format == 'geojson':
        params_part = '/'.join([str(param) for param in params])
        ci_report_url = f'data/{endpoint_name}_ci_report/{params_part}/{{x_idx}}/{{y_idx}}'
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

@app.route('/data/map/<function_name>')
@app.route('/data/map/<function_name>/<format>')
@get_cache().cached(timeout=60, query_string=True)
def data_new(function_name, format='geojson'):

    if not function_name in hazards:
        return "not found\n", 404

    hazard = hazards[function_name]

    args = parse_and_validate_args(hazard)
    if not args:
        return "Invalid arguments", 400

    print(args)

    hazard_function = hazard['function']
    composite_fit = init_composite_fit(
        app.config['DATA_FILE_DESC'],
        simParams='c,loc1,scale1',
        nVariates=1000,
        preProcess=True,
    )

    result = hazard_function(composite_fit, *args)
    
    return make_data_response(result, format, function_name, args)


@app.route('/data/ci_report/<function_name>/<x_idx>/<y_idx>')
@get_cache().cached(timeout=60, query_string=True)
def data_new(function_name, format='geojson'):

    if not function_name in hazards:
        return "not found\n", 404

    hazard = hazards[function_name]
    args = parse_and_validate_args(hazard)
    if not args:
        return "Invalid arguments", 400

    print(args)

    hazard_function = hazard['function']
    composite_fit = init_composite_fit(
        app.config['DATA_FILE_DESC'],
        simParams='c,loc1,scale1',
        nVariates=1000,
        preProcess=True,
    )

    result = hazard_function(composite_fit, *args)
    
    return make_data_response(result, format, function_name, args)


@app.route('/data/extreme_temp/intensity/<covariate>/<tauReturn>')
@app.route('/data/extreme_temp/intensity/<covariate>/<tauReturn>/<format>')
@get_cache().cached(timeout=50)
@validate_args(
    ('covariate', is_number, float),
    ('tauReturn', is_number, float),
    ('format', is_supported_format, str_lower),
)
def data_extreme_temp_intensity(covariate, tauReturn, format='geojson'):

    if format == 'geojson' and db.has_results(function='extreme_temp.intensity_from_return_time', covariate=covariate, return_time=tauReturn):
        return make_json_response(
            db.get_json_hazard_data(function='extreme_temp.intensity_from_return_time', covariate=covariate, return_time=tauReturn)
        )

    composite_fit = init_composite_fit(
        app.config['DATA_FILE_DESC'],
        simParams='c,loc1,scale1',
        nVariates=10000,
        preProcess=True,
    )

    intensity = intensity_from_return_time(composite_fit, covariate, tauReturn)

    # Make the response object
    return make_data_response(intensity, format, 'extreme_temp/intensity', (covariate, tauReturn))

@app.route('/data/extreme_temp/intensity_ci_report/<covariate>/<return_time>/<x_idx>/<y_idx>')
@get_cache().cached(timeout=50)
@validate_args(
    ('covariate', is_number, float),
    ('return_time', is_number, float),
    ('x_idx', is_number, int),
    ('y_idx', is_number, int),
)
def data_extreme_temp_intensity_ci_report(covariate, return_time, x_idx, y_idx):

    composite_fit = init_composite_fit(
        app.config['DATA_FILE_DESC'],
        simParams='c,loc1,scale1',
        nVariates=1000,
        preProcess=True,
    )
    result = intensity_ci_report(composite_fit, return_time, covariate, x_idx, y_idx)
    return result, 200

@app.route('/data/extreme_temp/return_time/<covariate>/<intensity>')
@app.route('/data/extreme_temp/return_time/<covariate>/<intensity>/<format>')
@get_cache().cached(timeout=50)
@validate_args(
    ('covariate', is_number, float),
    ('intensity', is_number, float),
    ('format', is_supported_format, str_lower),
)
def data_extreme_temp_return_time(covariate, intensity, format='geojson'):

    if format == 'geojson' and db.has_results(function='extreme_temp.return_time_from_intensity', covariate=covariate, intensity=intensity):
        return make_json_response(
            db.get_json_hazard_data(function='extreme_temp.return_time_from_intensity', covariate=covariate, intensity=intensity)
        )

    composite_fit = init_composite_fit(
        app.config['DATA_FILE_DESC'],
        simParams='c,loc1,scale1',
        nVariates=10000,
        preProcess=True,
    )

    return_time = return_time_from_intensity(composite_fit, covariate, intensity)
    # Make the response object
    return make_data_response(return_time, format, 'extreme_temp/return_time', (covariate, intensity))


@app.route('/data/extreme_temp/return_time_ci_report/<covariate>/<intensity>/<x_idx>/<y_idx>')
@get_cache().cached(timeout=50)
@validate_args(
    ('covariate', is_number, float),
    ('intensity', is_number, float),
    ('x_idx', is_number, int),
    ('y_idx', is_number, int),
)
def data_extreme_temp_return_time_ci_report(covariate, intensity, x_idx, y_idx):

    composite_fit = init_composite_fit(
        app.config['DATA_FILE_DESC'],
        simParams='c,loc1,scale1',
        nVariates=1000,
        preProcess=True,
    )
    result = return_time_ci_report(composite_fit, covariate, intensity, x_idx, y_idx)
    return result, 200


@app.route('/data/extreme_temp/intensity_change/<covariate0>/<return_time>/<covariate1>')
@app.route('/data/extreme_temp/intensity_change/<covariate0>/<return_time>/<covariate1>/<format>')
@get_cache().cached(timeout=50)
@validate_args(
    ('covariate0', is_number, float),
    ('return_time', is_number, float),
    ('covariate1', is_number, float),
    ('format', is_supported_format, str_lower),
)
def data_extreme_temp_intensity_change(covariate0, return_time, covariate1, format='geojson'):

    if covariate1 <= covariate0:
        return "covariate1 > covariate0 is required", 400

    if format == 'geojson' and db.has_results(function='extreme_temp.change_in_intensity', covariate=covariate0, covariate_comp=covariate1, return_time=return_time):
        return make_json_response(
            db.get_json_hazard_data(function='extreme_temp.change_in_intensity', covariate=covariate0, covariate_comp=covariate1, return_time=return_time)
        )

    composite_fit = init_composite_fit(
        app.config['DATA_FILE_DESC'],
        simParams='c,loc1,scale1',
        nVariates=1000,
        preProcess=True,
    )
    result = change_in_intensity(composite_fit, return_time, covariate0, covariate1)

    # Make the response object
    return make_data_response(result, format, 'extreme_temp/intensity_change', (covariate0, return_time, covariate1))

@app.route('/data/extreme_temp/intensity_change_ci_report/<covariate0>/<return_time>/<covariate1>/<x_idx>/<y_idx>')
@get_cache().cached(timeout=50)
@validate_args(
    ('covariate0', is_number, float),
    ('return_time', is_number, float),
    ('covariate1', is_number, float),
    ('x_idx', is_number, int),
    ('y_idx', is_number, int),
)
def data_extreme_temp_intensity_change_ci_report(covariate0, return_time, covariate1, x_idx, y_idx):

    if covariate1 <= covariate0:
        return "covariate1 > covariate0 is required", 400

    composite_fit = init_composite_fit(
        app.config['DATA_FILE_DESC'],
        simParams='c,loc1,scale1',
        nVariates=1000,
        preProcess=True,
    )
    result = change_in_intensity_ci_report(composite_fit, return_time, covariate0, covariate1, x_idx, y_idx)
    return result, 200

@app.route('/data/extreme_temp/frequency_change/<covariate0>/<intensity>/<covariate1>')
@app.route('/data/extreme_temp/frequency_change/<covariate0>/<intensity>/<covariate1>/<format>')
@get_cache().cached(timeout=50)
@validate_args(
    ('covariate0', is_number, float),
    ('intensity', is_number, float),
    ('covariate1', is_number, float),
    ('format', is_supported_format, str_lower),
)
def data_extreme_temp_frequency_change(covariate0, intensity, covariate1, format='geojson'):

    if covariate1 <= covariate0:
        return "covariate1 > covariate0 is required", 400

    if format == 'geojson' and db.has_results(function='extreme_temp.change_in_frequency', covariate=covariate0, covariate_comp=covariate1, intensity=intensity):
        return make_json_response(
            db.get_json_hazard_data(function='extreme_temp.change_in_frequency', covariate=covariate0, covariate_comp=covariate1, intensity=intensity)
        )

    composite_fit = init_composite_fit(
        app.config['DATA_FILE_DESC'],
        simParams='c,loc1,scale1',
        nVariates=1000,
        preProcess=True,
    )
    result = change_in_frequency(composite_fit, intensity, covariate0, covariate1)

    # Make the response object
    return make_data_response(result, format, 'extreme_temp/frequency_change', (covariate0, intensity, covariate1))


@app.route('/data/extreme_temp/frequency_change_ci_report/<covariate0>/<intensity>/<covariate1>/<x_idx>/<y_idx>')
@get_cache().cached(timeout=50)
@validate_args(
    ('covariate0', is_number, float),
    ('intensity', is_number, float),
    ('covariate1', is_number, float),
    ('x_idx', is_number, int),
    ('y_idx', is_number, int),
)
def data_extreme_temp_frequency_change_ci_report(covariate0, intensity, covariate1, x_idx, y_idx):

    if covariate1 <= covariate0:
        return "covariate1 > covariate0 is required", 400

    composite_fit = init_composite_fit(
        app.config['DATA_FILE_DESC'],
        simParams='c,loc1,scale1',
        nVariates=1000,
        preProcess=True,
    )
    result = change_in_frequency_ci_report(composite_fit, intensity, covariate0, covariate1, x_idx, y_idx)
    return result, 200

