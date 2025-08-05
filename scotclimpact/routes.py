from flask import current_app as app
from flask import render_template


def menu_items():
    return []

@app.route('/')
def index():
    return render_template(
        'map.html',
        navigation=menu_items(),
        mapserverurl=app.config['MAPSERVER_URL'],
        tilelayerurl=app.config['TILE_LAYER_URL'],
        mapattribs='[]',
        domains=[],
        years=[],
    )

