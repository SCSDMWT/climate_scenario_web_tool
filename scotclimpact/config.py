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

    BOUNDARY_LAYER_CACHE_DIR = os.environ.get(
        'BOUNDARY_LAYER_CACHE_DIR',
        'data/boundaries'
    )
    BOUNDARY_LAYER = dict(
        local_authorities=dict(
            url=os.environ.get('BL_COUNCIL_URL', ''),
            cache_file='local_council.json',
        ),
        fire_rescue=dict(
            url=os.environ.get('BL_FIRE_RESCUE_URL', ''),
            cache_file='fire_rescue.json',
        ),
        police=dict(
            url=os.environ.get('BL_POLICE_URL', ''),
            cache_file='police.json',
        ),
        health_integration_authorities=dict(
            url=os.environ.get('BL_HEALTH_INT_AUTH_URL', ''),
            cache_file='health_integration_authorities.json',
        ),
        health_boards=dict(
            url=os.environ.get('BL_HEALTH_BOARDS_URL', ''),
            cache_file='health_boards.json',
        ),
    )

    
