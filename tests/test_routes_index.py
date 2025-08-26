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
    response = client.get("/data/extreme_temp/intensity/2/100")

    assert response.status_code == 200
    assert b"extreme_temp/intensity" in response.data
    assert b"FeatureCollection" in response.data

def test_data_extreme_temp_intensity_change(client):
    '''The index should load the map, which contains the div and map.js'''
    response = client.get("/data/extreme_temp/intensity_change/2/100/4")

    assert response.status_code == 200
    assert b"extreme_temp/intensity_change" in response.data
    assert b"FeatureCollection" in response.data
