from flask import g, current_app
import pooch
import requests

DATA_REPO_VERSION = "v0.0.5"
GITHUB_API_URL = "https://api.github.com/repos/SCSDMWT/climate_scenario_web_tool_data/contents/"


def make_pooch(path=pooch.os_cache('scotclimpact')):
    '''Create the pooch object for the data repo'''
    return pooch.create(
        path=path,
        base_url=GITHUB_API_URL,
        version=DATA_REPO_VERSION,
        version_dev="main",
        registry={
            'boundaries/fire_rescue.json': 'md5:4fcfc1910ff0b14ff1a151539eb47fcb',
            'boundaries/health_boards.json': 'md5:c8d78c5ae40e9f2cd923f20011e4965c',
            'boundaries/health_integration_authorities.json': 'md5:ce33d6a6d1e48f856388e0a8bbbf3e9a',
            'boundaries/local_authorities.json': 'md5:5e0a3d394e402ffb52c5e9124ac359ab',
            'boundaries/police.json': 'md5:c380d0bbe3b1e503789222e87e601594',
            'extreme_temp/GEV_covaraite_fit_tasmax_linear_loc_scale_nFits_1000_parametric_False.nc': 'md5:145ebc6989207d4c96828e73978404a8',
            'extreme_temp/gridWide_g12.nc': 'md5:55857da3190275b0a0556717eccadc46',
            'extreme_temp/HadUK_GEV_covaraite_fit_tasmax_linear_loc_scale_nFits_1000_parametric_False.nc': 'md5:38b40faa92d9df4ac9b5128b9da6e840',
        },
    )

def get_pooch(app):
    '''Get the pooch object in the context of a Flask app'''
    if not 'pooch' in g:
        g.pooch = make_pooch(path=app.config['DATA_DIR'])
    return g.pooch


def from_private_github_repo(data_repo_github_token):
    '''A custom Pooch downloader to fetch files from a private github repository'''
    def _downloader(url, output_file, mypooch):
        api_request_headers = dict(
            Authorization=f"token {data_repo_github_token}",
        )
        r = requests.get(url + f'?ref={DATA_REPO_VERSION}', headers=api_request_headers)
        if not r.status_code == 200:
            print(f"[{r.status_code}] {r.text}")
            return

        download_url = r.json()['download_url']
        downloader = pooch.HTTPDownloader()
        downloader(download_url, output_file, mypooch)
    return _downloader


def fetch_file(filename):
    '''Downloads a file in the registry and returns it's local filename.'''
    pooch_ = get_pooch(current_app)
    return pooch_.fetch(
        filename, 
        downloader=from_private_github_repo(current_app.config['DATA_REPO_GITHUB_TOKEN'])
    )


def init_data(app):
    '''Ensure each data file is downloaded'''
    for file in get_pooch(app).registry:
        fetch_file(file)
