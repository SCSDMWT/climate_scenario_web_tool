import pytest
#from scotclimpact.projections import lat_lon_to_modis, modis_to_lat_lon
from scotclimpact.projections import Modis_1km 

TOL = 1e-13
modis_test_data = [
    (60, -20, 17, 3)
    #(-5, -42, 13, 9),
    #(-23.533773, -46.62529, 13, 11),
    #(0, 179, 35, 9),
    #(89, 179, 18, 0),
    #(-25.439538, 149.053418, 31, 11),
]

@pytest.mark.parametrize("lat, lon, h, v", modis_test_data)
def test_lat_lon_to_modis(lat, lon, h, v):
    real_h, real_v = Modis_1km.lat_lon_to_modis(lat, lon)
    assert abs(real_h - h) < TOL, f"returned {real_h}. expected {h}"
    assert abs(real_v - v) < TOL, f"returned {real_v}. expected {v}"


@pytest.mark.parametrize("lat, lon, h, v", modis_test_data)
def test_modis_to_lat_lon(lat, lon, h, v):
    '''See https://gis.stackexchange.com/a/337575'''
    real_lat, real_lon = Modis_1km.modis_to_lat_lon(h, v)
    print(lat, lon, h, v, real_lat, real_lon)
    assert abs(real_lat - lat) < TOL, f"returned: {real_lat}. expected: {lat}"
    assert abs(real_lon - lon) < TOL, f"returned: {real_lon}. expected: {lon}"


def gen_test_data():
    pass
