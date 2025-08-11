import functools
import io
import json

from flask import current_app as app
from flask import render_template, make_response, send_file

from .extreme_temp import init_composite_fit, intensity_from_return_time
from .data_helpers import xarray_to_geojson

def menu_items():
    return []

@app.route('/')
def index():
    return render_template(
        'map.html',
        navigation=menu_items(),
        mapserverurl=app.config['MAPSERVER_URL'],
        tilelayerurl=app.config['TILE_LAYER_URL'],
    )

@app.route('/data/extreme_temp/intensity/<covariate>/<tauReturn>')
def data_extreme_temp_intensity(covariate, tauReturn):
    composite_fit = init_composite_fit(
        app.config['DATA_FILE_DESC'],
        simParams='c,loc1,scale1',
        nVariates=10000,
        preProcess=False,
    )
    covariate = float(covariate)
    tauReturn = int(tauReturn)
    intensity = intensity_from_return_time(composite_fit, covariate, tauReturn)

    # Make the response object
    json_data = xarray_to_geojson('extreme_temp/intensity', intensity)
    json_str = json.dumps(json_data)

    response = make_response(send_file(
        io.BytesIO(json_str.encode('utf-8')), 
        mimetype='application/json'
    ))
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response
