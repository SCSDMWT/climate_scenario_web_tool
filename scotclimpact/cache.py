from flask import current_app, g
from flask_caching import Cache

def get_cache():
    if not 'cache' in g:
        g.cache = Cache(current_app)
    return g.cache
    
