import geopandas as gpd
import functools

@functools.lru_cache(maxsize=8)
def get_wfs(url, tolerance=10000):
    '''Read geojson file and simplify it's resolution'''
    gdf = gpd.read_file(url)
    gdf['geometry'] = gdf.geometry.simplify(tolerance, preserve_topology=True)
    return gdf.to_json()

