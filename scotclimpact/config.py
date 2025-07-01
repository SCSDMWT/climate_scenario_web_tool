import os

class Config:
    '''Set Flask configuration variables'''
    MAPSERVER_URL = os.environ.get(
        'MAPSERVER_URL',
        'http://0.0.0.0?/etc/mapserver/scotclimpact.map'
    )
    DATABASE_URL = os.environ.get(
        'DATABASE_URL',
        'postgresql://scotclimpact:testingtesting@localhost/scotclimpact'
    )
