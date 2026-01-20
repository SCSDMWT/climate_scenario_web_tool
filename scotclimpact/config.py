import os

import pooch

class Config:
    '''Set Flask configuration variables'''

    ## Caching
    DEBUG = True
    PROFILE = os.environ.get('PROFILE', False)
    CACHE_TYPE = os.environ.get('CACHE_TYPE', 'SimpleCache')
    CACHE_DEFAULT_TIMEOUT = os.environ.get('CACHE_DEFAULT_TIMEOUT', 300)


    ## External services
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

    ## Input Datasets
    DATA_DIR = os.environ.get(
        'DATA_DIR',
        pooch.os_cache('scotclimpact'),
    )

    GTAG_ID = os.environ.get(
        'GTAG_ID',
        '',
    )
