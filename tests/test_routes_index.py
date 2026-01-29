import pytest

import xarray as xr

from scotclimpact.data_helpers import xarray_to_geojson

from fixtures import client, test_app, pooch_fetcher

def test_index(client):
    '''The index should load the map, which contains the div and map.js'''
    response = client.get("/")

    assert response.status_code == 200
    assert b"<div id='map' class='map'></div>" in response.data
    assert b"src=\"/static/dist/main.js\"" in response.data


def test_data_extreme_temp(client):
    '''The index should load the map, which contains the div and map.js'''
    response = client.get(
        "/data/map/extreme_temp_intensity",
        query_string=dict(covariate=2, return_time=100),
    )

    assert response.status_code == 200
    assert b"extreme_temp_intensity" in response.data
    assert b"FeatureCollection" in response.data

def test_data_extreme_temp_intensity_change(client):
    '''The index should load the map, which contains the div and map.js'''
    response = client.get(
        "/data/map/extreme_temp_intensity_change",
        query_string=dict(covariate=2.0, return_time=100, covariate_comp=1.5),
    )

    assert response.status_code == 200
    assert b"extreme_temp_intensity_change" in response.data
    assert b"FeatureCollection" in response.data

#def test_data_extreme_temp_intensity_change_inv_cov(client):
#    '''Invalid pair of cavariate values (covariateComp should be less than covariate) should return HTTP 400'''
#    response = client.get(
#        "/data/map/extreme_temp_intensity_change",
#        query_string=dict(covariate=2, return_time=100, covariate_comp=2.5),
#    )
#
#    assert response.status_code == 400

def test_data_extreme_temp_frequency_change(client):
    '''The index should load the map, which contains the div and map.js'''
    response = client.get(
        "/data/map/extreme_temp_frequency_change",
        query_string=dict(covariate=2, intensity=30, covariate_comp=1.5),
    )

    assert response.status_code == 200
    assert b"extreme_temp_frequency_change" in response.data
    assert b"FeatureCollection" in response.data

#def test_data_extreme_temp_frequency_change_inv_cov(client):
#    '''Invalid pair of cavariate values (covariateComp should be less than covariate) should return HTTP 400'''
#    response = client.get(
#        "/data/map/extreme_temp_frequency_change",
#        query_string=dict(covariate=2, intensity=30, covariate_comp=2.5),
#    )
#
#    assert response.status_code == 400

@pytest.fixture()
def test_nc_data(pooch_fetcher):
    filename = pooch_fetcher('model_fits/obs/GEV_covaraite_fit_HadUK_tasmax_linear_loc_log_scale_nFits_1000_parametric_False.nc')
    data = xr.load_dataset(filename)
    return data['tasmax'][:, 0, :].T # just need to select a slice of 'tasmax' that contain some non-nan values and is a variable of x and y coordinates


def test_xarray_to_geojson(test_nc_data, test_app):
    with test_app.app_context():
        json = xarray_to_geojson('test', test_nc_data)

    assert type(json) == type({})
    assert 'type' in json and json['type'] == 'FeatureCollection'
    assert 'name' in json and json['name'] == 'test'
    assert 'crs' in json and 'properties' in json['crs'] and 'name' in json['crs']['properties'] 
    assert '27700' in json['crs']['properties']['name']

    assert 'features' in json
    assert type(json['features']) == type([])
    assert len(json['features']) > 0
    assert 'type' in json['features'][0] and json['features'][0]['type'] == 'Feature'

    assert 'properties' in json['features'][0]

    assert 'geometry' in json['features'][0]
    assert 'type' in json['features'][0]['geometry'] and json['features'][0]['geometry']['type'] == 'Polygon'
    assert 'coordinates' in json['features'][0]['geometry'] and len(json['features'][0]['geometry']['coordinates']) == 1

    assert len(json['features'][0]['geometry']['coordinates'][0][0]) > 0
    #assert type(json['features'][0]['geometry']['coordinates'][0][0]) == np.float64


