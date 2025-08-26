import os

import pooch

class Config:
    '''Set Flask configuration variables'''

    ## Caching
    DEBUG = True
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
    DATA_USERNAME = os.environ.get('DATA_USERNAME', '')
    DATA_PASSWORD = os.environ.get('DATA_PASSWORD', '')
    DATA_DIR = os.environ.get(
        'DATA_DIR',
        pooch.os_cache('scotclimpact'),
    )
    DATA_FILE_DESC = 'GEV_covaraite_fit_tasmax_linear_loc_scale_nFits_1000_parametric_False'

    ## Boundary layer data
    BOUNDARY_LAYER_CACHE_DIR = os.environ.get(
        'BOUNDARY_LAYER_CACHE_DIR',
        'data/boundaries'
    )
    BOUNDARY_LAYER = dict(
        local_authorities=dict(
            url=os.environ.get(
                'BL_COUNCIL_URL',
                'https://geo.spatialhub.scot/geoserver/sh_las/wfs?authkey=b85aa063-d598-4582-8e45-e7e6048718fc&request=GetFeature&service=WFS&version=1.1.0&outputFormat=application%2Fjson&typeName=pub_las'
            ),
            cache_file='local_council.json',
        ),
        fire_rescue=dict(
            url=os.environ.get(
                'BL_FIRE_RESCUE_URL', 
                'https://maps.gov.scot/server/services/ScotGov/CrimeJusticeSafety/MapServer/WFSServer?typename=CJS:ScottishFireRescue&request=GetFeature&service=WFS&version=1.1.0'
            ),
            cache_file='fire_rescue.json',
        ),
        police=dict(
            url=os.environ.get(
                'BL_POLICE_URL',
                'https://maps.gov.scot/server/services/ScotGov/CrimeJusticeSafety/MapServer/WFSServer?typename=CJS:ScottishPoliceDivisions&request=GetFeature&service=WFS&version=1.1.0'
            ),
            cache_file='police.json',
        ),
        health_integration_authorities=dict(
            url=os.environ.get(
                'BL_HEALTH_INT_AUTH_URL',
                'https://maps.gov.scot/server/services/ScotGov/CrimeJusticeSafety/MapServer/WFSServer?typename=CJS:ScottishPoliceDivisions&request=GetFeature&service=WFS&version=1.1.0'
            ),
            cache_file='health_integration_authorities.json',
        ),
        health_boards=dict(
            url=os.environ.get(
                'BL_HEALTH_BOARDS_URL', 
                'https://maps.gov.scot/server/services/ScotGov/HealthSocialCare/MapServer/WFSServer?typename=HSC:NHSHealthBoards&request=GetFeature&service=WFS&version=1.1.0'
            ),
            cache_file='health_boards.json',
        ),
    )

    
