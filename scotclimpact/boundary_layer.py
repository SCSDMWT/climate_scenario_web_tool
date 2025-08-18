import geopandas as gpd
import functools
import os

@functools.lru_cache(maxsize=8)
def get_wfs(url, cache_file, tolerance=1000):
    '''Read geojson file and simplify it's resolution'''
    if os.path.exists(cache_file):
        gdf = gpd.read_file(cache_file)
    else:
        gdf = gpd.read_file(url)
        with open(cache_file, 'w') as file:
            file.write(gdf.to_json())

    #gdf['geometry'] = gdf.geometry.simplify(tolerance, preserve_topology=True)
    return gdf.to_json()

