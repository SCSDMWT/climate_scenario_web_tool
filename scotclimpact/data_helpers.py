import numpy as np
import xarray as xr

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
                data=value
            ),
            geometry=dict(
                type='Polygon',
                coordinates=[[tr, tl, bl, br, tr]],
            ),
        )
        for tr, tl, br, bl, value in zip(top_right, top_left, bottom_right, bottom_left, dataset[idx])
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
