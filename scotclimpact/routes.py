import io
import json
import os

from flask import current_app as app
from flask import render_template, make_response, send_file

from .extreme_temp import (
    init_composite_fit,
    intensity_from_return_time,
    return_time_from_intensity,
    change_in_intensity,
    change_in_frequency,
)
from .data_helpers import xarray_to_geojson, is_number
from .boundary_layer import is_valid_boundary_layer, get_boundary_layer
from .cache import get_cache

def menu_items():
    return []

@app.route('/')
@get_cache().cached(timeout=50)
def index():
    return render_template(
        'map.html',
        navigation=menu_items(),
        mapserverurl=app.config['MAPSERVER_URL'],
        tilelayerurl=app.config['TILE_LAYER_URL'],
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
def make_data_response(dataset, format, endpoint_name, params):
    # Make the response object
    if format == 'geojson':
        json_data = xarray_to_geojson(endpoint_name, dataset)
        return make_json_response(json_data)
    if format == 'netcdf':
        return make_netcdf_response(dataset, endpoint_name, params)
    if format == 'csv':
        return make_csv_response(dataset, endpoint_name, params)


@app.route('/boundaries/<layer_name>')
@get_cache().cached(timeout=50)
def bondaries_local_authorities(layer_name):
    if not is_valid_boundary_layer(layer_name):
        return 'Not found', 404
    return get_boundary_layer(layer_name)

@app.route('/data/extreme_temp/intensity/<covariate>/<tauReturn>')
@app.route('/data/extreme_temp/intensity/<covariate>/<tauReturn>/<format>')
@get_cache().cached(timeout=50)
def data_extreme_temp_intensity(covariate, tauReturn, format='geojson'):

    if not is_number(covariate):
        app.logger.warn("Covariate must be float. Got {covariate}")
        return "Covariate must be float", 400
    if not is_number(tauReturn):
        app.logger.warn("tauReturn must be int. Got {tauReturn}")
        return "tauReturn must be int", 400
    format = format.lower()
    if not format in SUPPORTED_FORMATS:
        return f"format must be one of {SUPPORTED_FORMATS}. Recieved {format}", 400

    composite_fit = init_composite_fit(
        app.config['DATA_FILE_DESC'],
        simParams='c,loc1,scale1',
        nVariates=10000,
        preProcess=False,
    )
    tauReturn = int(tauReturn)
    covariate = float(covariate)

    intensity = intensity_from_return_time(composite_fit, covariate, tauReturn)

    # Make the response object
    return make_data_response(intensity, format, 'extreme_temp/intensity', (covariate, tauReturn))


@app.route('/data/extreme_temp/return_time/<covariate>/<intensity>')
@app.route('/data/extreme_temp/return_time/<covariate>/<intensity>/<format>')
@get_cache().cached(timeout=50)
def data_extreme_temp_return_time(covariate, intensity, format='geojson'):

    if not is_number(covariate):
        app.logger.warn("Covariate must be float. Got {covariate}")
        return "Covariate must be float", 400
    if not is_number(intensity):
        app.logger.warn("Intensity must be int. Got {tauReturn}")
        return "Intensity must be int", 400
    format = format.lower()
    if not format in SUPPORTED_FORMATS:
        return f"format must be one of {SUPPORTED_FORMATS}. Recieved {format}", 400

    composite_fit = init_composite_fit(
        app.config['DATA_FILE_DESC'],
        simParams='c,loc1,scale1',
        nVariates=10000,
        preProcess=False,
    )
    intensity = int(intensity)
    covariate = float(covariate)

    return_time = return_time_from_intensity(composite_fit, covariate, intensity)

    # Make the response object
    return make_data_response(return_time, format, 'extreme_temp/return_time', (covariate, intensity))


@app.route('/data/extreme_temp/intensity_change/<covariate0>/<return_time>/<covariate1>')
@app.route('/data/extreme_temp/intensity_change/<covariate0>/<return_time>/<covariate1>/<format>')
@get_cache().cached(timeout=50)
def data_extreme_temp_intensity_change(covariate0, return_time, covariate1, format='geojson'):
    if not is_number(covariate0):
        return "Covariate0 must be float", 400
    if not is_number(covariate1):
        return "Covariate1 must be float", 400
    if not is_number(return_time):
        return "return_time must be int", 400
    format = format.lower()
    if not format in SUPPORTED_FORMATS:
        return f"format must be one of {SUPPORTED_FORMATS}. Recieved {format}", 400

    covariate0 = float(covariate0)
    covariate1 = float(covariate1)
    return_time = float(return_time)

    if covariate1 <= covariate0:
        return "covariate1 > covariate0 is required", 400

    composite_fit = init_composite_fit(
        app.config['DATA_FILE_DESC'],
        simParams='c,loc1,scale1',
        nVariates=1000,
        preProcess=True,
    )
    result = change_in_intensity(composite_fit, return_time, covariate0, covariate1)

    # Make the response object
    return make_data_response(result, format, 'extreme_temp/intensity_change', (covariate0, return_time, covariate1))


@app.route('/data/extreme_temp/frequency_change/<covariate0>/<intensity>/<covariate1>')
@app.route('/data/extreme_temp/frequency_change/<covariate0>/<intensity>/<covariate1>/<format>')
@get_cache().cached(timeout=50)
def data_extreme_temp_frequency_change(covariate0, intensity, covariate1, format='geojson'):
    if not is_number(covariate0):
        return "Covariate0 must be float", 400
    if not is_number(covariate1):
        return "Covariate1 must be float", 400
    if not is_number(intensity):
        return "intensity must be int", 400
    format = format.lower()
    if not format in SUPPORTED_FORMATS:
        return f"format must be one of {SUPPORTED_FORMATS}. Recieved {format}", 400

    covariate0 = float(covariate0)
    covariate1 = float(covariate1)
    intensity = float(intensity)

    if covariate1 <= covariate0:
        return "covariate1 > covariate0 is required", 400

    composite_fit = init_composite_fit(
        app.config['DATA_FILE_DESC'],
        simParams='c,loc1,scale1',
        nVariates=1000,
        preProcess=True,
    )
    result = change_in_frequency(composite_fit, intensity, covariate0, covariate1)

    # Make the response object
    return make_data_response(result, format, 'extreme_temp/frequency_change', (covariate0, intensity, covariate1))

