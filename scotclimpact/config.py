import os

class Config:
    '''Set Flask configuration variables'''
    MAPSERVER_URL = os.environ.get(
        'MAPSERVER_URL',
        'http://127.0.0.1:8080?/etc/mapserver/scotclimpact.map'
    )
    DATABASE_URL = os.environ.get(
        'DATABASE_URL',
        'postgresql://scotclimpact:testingtesting@localhost/scotclimpact'
    )
    TILE_LAYER_URL = os.environ.get(
        'TILE_LAYER_URL',
        ''
    )
    DATA_FILE_DESC = 'GEV_covaraite_fit_tasmax_linear_loc_scale_nFits_1000_parametric_False'
    
