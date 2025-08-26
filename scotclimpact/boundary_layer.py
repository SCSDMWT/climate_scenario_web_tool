from flask import current_app

from .data import get_pooch

def is_valid_boundary_layer(layer_name):
    '''Returns True if layer_name is a valid boundary layer.'''
    pooch = get_pooch(current_app)
    return f'boundaries/{layer_name}.json' in pooch.registry

def get_boundary_layer(layer_name):
    '''Loads the GeoJSON content of a boundary layer.'''
    pooch = get_pooch(current_app)
    local_filename = pooch.fetch(f'boundaries/{layer_name}.json')
    with open(local_filename, 'r') as file:
        return file.read()
