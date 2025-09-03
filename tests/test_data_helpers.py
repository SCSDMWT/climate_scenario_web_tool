import pytest

import xarray as xr

from scotclimpact.data_helpers import xarray_to_geojson, is_number
#from scotclimpact.data import fetch_files
from fixtures import pooch


@pytest.mark.parametrize(
    ('input', 'result'),
    [
        ('', False),
        ('1a', False),
        ('.', False),
        ('1', True),
        ('12', True),
        ('1.1', True),
        ('11.1', True),
        ('11.21', True),
        ('11.', True),
        ('.11', True),
        ('11.21.', False),
        ('11.21.5', False),
        ('NaN', False),
        ('Inf', False),
        ('-Inf', False),
    ]
)
def test_is_number(input, result):
    result and float(input) # if result is True, float should not throw exceptions
    assert is_number(input) == result 


@pytest.fixture()
def test_nc_data(pooch):
    filename = pooch.fetch('extreme_temp/GEV_covaraite_fit_tasmax_linear_loc_scale_nFits_1000_parametric_False.nc')
    data = xr.load_dataset(filename)
    return data['tasmax'][:, :, 0, 0]


def test_xarray_to_geojson(test_nc_data):
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


