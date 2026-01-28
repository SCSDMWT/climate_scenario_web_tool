from flask import current_app
import shapely
import functools
import json

from .data import get_pooch, fetch_file

def is_valid_boundary_layer(layer_name):
    '''Returns True if layer_name is a valid boundary layer.'''
    pooch = get_pooch(current_app)
    return f'boundaries/{layer_name}.json' in pooch.registry

def get_boundary_layer(layer_name):
    '''Loads the GeoJSON content of a boundary layer.'''
    local_filename = fetch_file(f'boundaries/{layer_name}.json')
    with open(local_filename, 'r') as file:
        return file.read()

@functools.lru_cache(maxsize=1)
def get_scotland_shape():
    '''Calculate a shape for Scotland by taking the union of health board shapes'''
    health_boards_txt = get_boundary_layer("health_boards")
    health_boards_json = json.loads(health_boards_txt)
    health_boards_shp = [
        shapely.geometry.shape(feature)
        for feature in health_boards_json['features']
    ]
    return shapely.coverage_union_all(health_boards_shp)

def in_scotland(bounds):
    '''Predicate to determine if a rectangular region overlaps with Scotland'''
    scotland = get_scotland_shape()
    region = shapely.geometry.Polygon(bounds + [bounds[0]])
    return shapely.intersects(scotland, region)
    
