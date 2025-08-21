import geopandas as gpd
import os


def get_wfs(url, cache_file, tolerance=1000):
    '''Read geojson file and simplify it's resolution'''
    if not os.path.exists(cache_file):
        gdf = gpd.read_file(url)
        with open(cache_file, 'w') as file:
            file.write(gdf.to_json())
        
    with open(cache_file, 'r') as file:
        return file.read()
