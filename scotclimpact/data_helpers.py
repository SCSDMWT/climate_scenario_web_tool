from functools import wraps
import numpy as np
import re
import xarray as xr

def is_number(s):
    '''Returns true if s is a string representing an actual number (excluding NaN or Inf)'''
    return re.match(r'(^\d+(\.\d*)?$)|(^\.\d+$)', s) is not None

def validate_args(*types):
    '''A decorator to validate route variables/arguments. Route variables are passed as 
    arguments of type str, but often needs to be validated and converted to other formats. 
    This decorator takes a series of tuples (var_name, validator, converter) where
      * var_name is the variable/argument name
      * validator is a predicate to check if the variable has a valid value
      * converter is a function to turn the argument into the expected type.
    '''
    kw_types = {
        type_[0]: type_
        for type_ in types
    }
    def decorator(func):
        @wraps(func)
        def wrapper(*f_args, **f_kwargs):
            print(f_args, f_kwargs)

            converted_args = []
            for arg, type_ in zip(f_args, types):
                arg_name, checker, converter = type_
                if not checker(arg):
                    return f'Incorrect type {arg_name}', 400
                converted_args.append(converter(arg))
            converted_kwargs = {}
            for arg_name in f_kwargs:
                arg = f_kwargs[arg_name]
                _, checker, converter = kw_types[arg_name]
                if not checker(arg):
                    return f'Incorrect type {arg_name}', 400
                converted_kwargs[arg_name] = converter(arg)

            
            return func(*converted_args, **converted_kwargs)
        return wrapper
    return decorator


def str_lower(s):
    return s.lower()


def xarray_to_geojson(dataset_name, dataset, x_key='projection_x_coordinate', y_key='projection_y_coordinate'):
    '''Convert an xarray.DataArray object to GeoJSON compatible object.'''
    x_dim = dataset[x_key].to_numpy()
    y_dim = dataset[y_key].to_numpy()

    # Load the data
    dataset = dataset.to_numpy()
    idx = np.where(dataset == dataset)

    dx = np.diff(x_dim).min()/2.0
    dy = np.diff(y_dim).min()/2.0

    top_right =    [ [x_dim[i]+dx, y_dim[j]+dy] for j, i in zip(*idx)]
    top_left  =    [ [x_dim[i]+dx, y_dim[j]-dy] for j, i in zip(*idx) ]
    bottom_right = [ [x_dim[i]-dx, y_dim[j]+dy] for j, i in zip(*idx) ]
    bottom_left  = [ [x_dim[i]-dx, y_dim[j]-dy] for j, i in zip(*idx) ]

    # Create the geometry features
    features = [
        dict(
            type='Feature',
            properties=dict(
                data=value if not value == float("inf") else 10000,
                x_idx=int(coord_idx[0]),
                y_idx=int(coord_idx[1]),
            ),
            geometry=dict(
                type='Polygon',
                coordinates=[[tr, tl, bl, br, tr]],
            ),
        )
        for tr, tl, br, bl, value, coord_idx 
        in zip(top_right, top_left, bottom_right, bottom_left, dataset[idx], zip(*idx))
    ]

    crs = dict(
        type='name',
        properties=dict(
            name="urn:ogc:def:crs:EPSG::27700"
        )
    )

    return dict(
        type='FeatureCollection',
        numberMatched=len(features),
        name=dataset_name,
        features=features,
        crs=crs,
    )
