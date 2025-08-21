import io
import json
import os

from flask import current_app as app
from flask import render_template, make_response, send_file

from .extreme_temp import (
    init_composite_fit,
    intensity_from_return_time,
    return_time_from_intensity,
)
from .data_helpers import xarray_to_geojson, is_number
from .boundary_layer import get_wfs
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

@app.route('/boundaries/<layer_name>')
@get_cache().cached(timeout=50)
def bondaries_local_authorities(layer_name):
    if not layer_name in app.config['BOUNDARY_LAYER'] or app.config['BOUNDARY_LAYER'][layer_name]['url'] == '':
        return 'Not found', 404

    url = app.config['BOUNDARY_LAYER'][layer_name]['url']
    cache_file = os.path.join(
        app.config['BOUNDARY_LAYER_CACHE_DIR'],
        app.config['BOUNDARY_LAYER'][layer_name]['cache_file']
    )
    return make_json_response(get_wfs(url, cache_file))

@app.route('/data/extreme_temp/intensity/<covariate>/<tauReturn>')
@get_cache().cached(timeout=50)
def data_extreme_temp_intensity(covariate, tauReturn):

    if not is_number(covariate):
        app.logger.warn("Covariate must be float. Got {covariate}")
        return "Covariate must be float", 400
    if not is_number(tauReturn):
        app.logger.warn("tauReturn must be int. Got {tauReturn}")
        return "tauReturn must be int", 400

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
    json_data = xarray_to_geojson('extreme_temp/intensity', intensity)
    return make_json_response(json_data)

@app.route('/data/extreme_temp/return_time/<covariate>/<intensity>')
@get_cache().cached(timeout=50)
def data_extreme_temp_return_time(covariate, intensity):

    if not is_number(covariate):
        app.logger.warn("Covariate must be float. Got {covariate}")
        return "Covariate must be float", 400
    if not is_number(intensity):
        app.logger.warn("Intensity must be int. Got {tauReturn}")
        return "Intensity must be int", 400

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
    json_data = xarray_to_geojson('extreme_temp/return_time', return_time)
    return make_json_response(json_data)

