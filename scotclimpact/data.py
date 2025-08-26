from flask import g
import pooch

DATA_REPO_VERSION = "v0.0.1+dev"

#POOCH = pooch.create(
#    path=app.config['DATA_DIR'],
#    base_url="https://raw.githubusercontent.com/SCSDMWT/climate_scenario_web_tool_data/{version}",
#    version=DATA_REPO_VERSION,
#    version_dev="main",
#    registry={
#        'registry.txt': 'md5:',
#    }
#)
#POOCH.load_regitry(POOCH.fetch("registry.txt"))
def get_pooch(app):
    if not 'pooch' in g:
        g.pooch = pooch.create(
            path=app.config['DATA_DIR'],
            base_url="https://media.githubusercontent.com/media/SCSDMWT/climate_scenario_web_tool_data/{version}",
            #base_url="https://raw.githubusercontent.com/SCSDMWT/climate_scenario_web_tool_data/{version}",
            version=DATA_REPO_VERSION,
            version_dev="main",
            registry={
                'boundaries/fire_rescue.json': None, #'md5:4fcfc1910ff0b14ff1a151539eb47fcb',
                'boundaries/health_boards.json': 'md5:c8d78c5ae40e9f2cd923f20011e4965c',
                'boundaries/health_integration_authorities.json': 'md5:ce33d6a6d1e48f856388e0a8bbbf3e9a',
                'boundaries/local_council.json': 'md5:5e0a3d394e402ffb52c5e9124ac359ab',
                'boundaries/police.json': 'md5:c380d0bbe3b1e503789222e87e601594',
            },
        )
    return g.pooch

def init_data(app):
    #breakpoint()
    downloader = pooch.HTTPDownloader()
    for file in get_pooch(app).registry:
        get_pooch(app).fetch(file, downloader=downloader)
    
