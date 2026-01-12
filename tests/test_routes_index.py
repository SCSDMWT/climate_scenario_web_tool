import pytest

from fixtures import client, test_app


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
