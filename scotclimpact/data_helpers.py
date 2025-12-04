from functools import wraps
import json
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

def _make_bounds(dataset, idx, x_key, y_key):
    '''Calculate the 4 corners for cells from the grid of points.'''
    x_dim = dataset[x_key].to_numpy()
    y_dim = dataset[y_key].to_numpy()

    dx = np.diff(x_dim).min()/2.0
    dy = np.diff(y_dim).min()/2.0

    top_right =    [ [float(x_dim[i]+dx), float(y_dim[j]+dy)] for i, j in zip(*idx)]
    top_left  =    [ [float(x_dim[i]+dx), float(y_dim[j]-dy)] for i, j in zip(*idx) ]
    bottom_right = [ [float(x_dim[i]-dx), float(y_dim[j]+dy)] for i, j in zip(*idx) ]
    bottom_left  = [ [float(x_dim[i]-dx), float(y_dim[j]-dy)] for i, j in zip(*idx) ]

    return top_right, top_left, bottom_right, bottom_left

def _fix_infs(np_array, multiplier=1000):
    '''Update all 'inf' values of an np array to be multiplier * max(np_array)'''
    infs = np_array == float('inf')
    inf_idx = np.where(infs)
    proper_numbers_idx = np.where( (np_array == np_array) & ~infs )
    np_array[inf_idx] = multiplier * np.max(np_array)

def unwrap_xarray(xr_dataset, x_key='projection_x_coordinate', y_key='projection_y_coordinate'):
    '''Convert a grid of 2D cells to a list of containing only the points in the grid with values.'''

    np_dataset = xr_dataset.to_numpy()
    _fix_infs(np_dataset)
    idx = np.where(np_dataset == np_dataset)

    top_right, top_left, bottom_right, bottom_left = _make_bounds(xr_dataset, idx, x_key, y_key)
    geometries = [
        (tr, tl, br, bl)
        for tr, tl, br, bl
        in zip(top_right, top_left, bottom_right, bottom_left)
    ]
    return [
        dict(
            central_estimate=central_estimate,
            coord_idx=coord_idx,
            geometry_coords=geometry,
        )
        for central_estimate, coord_idx, geometry 
        in zip(np_dataset[idx], zip(*idx), geometries)
    ]

def unwrapped_xarray_to_sql(function_name, unwrapped_dataset, argument_values):
    '''Convert an unwrapped xarray.DataArray list to a list of VALUES clauses for an SQL query.'''

    def sql_coord_format(coord):
        return f"{coord[0]} {coord[1]}"

    def geometry_coords_to_sql(coords):
        tr, tl, br, bl = [
            sql_coord_format(coord)
            for coord in coords
        ]
        return f"ST_GeomFromText('POLYGON(({tr}, {tl}, {bl}, {br}, {tr}))', 27700)"

    argument_values_entry = ', '.join(map(str, argument_values))

    def entry_to_sql(central_estimate=0.0, geometry_coords='', coord_idx=[0, 0], ci_report_url=''):
        geometry = geometry_coords_to_sql(geometry_coords)
        return f"('{function_name}', {central_estimate}, {geometry}, {coord_idx[0]}, {coord_idx[1]}, '{ci_report_url}', {argument_values_entry})"

    values_clauses = [
        entry_to_sql(**entry)
        for entry in unwrapped_dataset
    ]

    return values_clauses

def sql_to_geojson(function_name, query_result):
    '''Converts a database query result (list of tuples) to GeoJSON.'''
    def psql_to_geojson(geojson):
        result = json.loads(geojson)
        result.pop('crs')
        return result

    features = [
        dict(
            type='Feature',
            properties=dict(
                data=result[0],
                ci_report_url=result[2],
            ),
            geometry=psql_to_geojson(result[1]),
        )
        for result in query_result
    ]

    crs = dict(
        type='name',
        properties=dict(
            name="urn:ogc:def:crs:EPSG::27700"
        )
    )

    return dict(
        type='FeatureCollection',
        numberMatched=len(query_result),
        name=function_name,
        features=features,
        crs=crs,
    )


def xarray_to_geojson(dataset_name, xr_dataset, x_key='projection_x_coordinate', y_key='projection_y_coordinate', ci_report_url=lambda x: x):
    '''Convert an xarray.DataArray object to GeoJSON compatible object.'''
    # Load the data
    np_dataset = xr_dataset.to_numpy()
    idx = np.where(np_dataset == np_dataset)

    top_right, top_left, bottom_right, bottom_left = _make_bounds(xr_dataset, idx, x_key, y_key)

    # Create the geometry features
    features = [
        dict(
            type='Feature',
            properties=dict(
                data=value if not value == float("inf") else 10000,
                ci_report_url=ci_report_url(x_idx=int(coord_idx[0]), y_idx=int(coord_idx[1])),
            ),
            geometry=dict(
                type='Polygon',
                coordinates=[[tr, tl, bl, br, tr]],
            ),
        )
        for tr, tl, br, bl, value, coord_idx 
        in zip(top_right, top_left, bottom_right, bottom_left, np_dataset[idx], zip(*idx))
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
