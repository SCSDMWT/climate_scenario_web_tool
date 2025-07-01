from pyproj import Proj

import math


def call_init_projection(cls):
    if getattr(cls, "init_projection", None):
        cls.init_projection()
    return cls

#@call_init_proj
class Modis:
    '''A base class for MODIS projections'''

    '''See https://gis.stackexchange.com/a/337575'''

    @classmethod
    def init_projection(cls):
        #CELLS = 1200
        #CELLS = 1200
        cls.VERTICAL_TILES = 18
        cls.HORIZONTAL_TILES = 36
        cls.EARTH_RADIUS = 6371007.181
        cls.EARTH_WIDTH = 2 * math.pi * cls.EARTH_RADIUS
        
        cls.TILE_WIDTH = cls.EARTH_WIDTH / cls.HORIZONTAL_TILES
        cls.TILE_HEIGHT = cls.TILE_WIDTH
        #cls.CELL_SIZE = cls.TILE_WIDTH / cls.CELLS
        cls.MODIS_GRID = Proj(f'+proj=sinu +R={cls.EARTH_RADIUS} +nadgrids=@null +wktext')
    
    
    @classmethod
    def lat_lon_to_modis(cls, lat, lon):
        '''Convert latitude/longitude to MODIS coordinates'''
        x, y = cls.MODIS_GRID(lon, lat)
        h = (cls.EARTH_WIDTH * .5 + x) / cls.TILE_WIDTH
        v = -(cls.EARTH_WIDTH * .25 + y - (cls.VERTICAL_TILES - 0) * cls.TILE_HEIGHT) / cls.TILE_HEIGHT
        print(lat, lon, h, v)
        return int(h), int(v)
    
    
    @classmethod
    def modis_to_lat_lon(cls, h, v):
        '''Convert modis coordinates to degrees lon/lat'''
        x = h * cls.TILE_WIDTH - cls.EARTH_WIDTH * .5
        y = - v * cls.TILE_HEIGHT - cls.EARTH_WIDTH * 0.25 + (cls.VERTICAL_TILES - 0) * cls.TILE_HEIGHT
        lon, lat = cls.MODIS_GRID(x, y, inverse=True)
        return (lat, lon)


@call_init_projection
class Modis_1km(Modis):
    CELLS = 1200

    #@classmethod
    #def init_projection(cls):
    #    cls._init_projection()

