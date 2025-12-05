from flask import g, current_app
import pooch
import requests

DATA_REPO_VERSION = "v0.0.5+dev"
GITHUB_API_URL = "https://media.githubusercontent.com/media/SCSDMWT/climate_scenario_web_tool_data/{version}"
#"https://api.github.com/repos/SCSDMWT/climate_scenario_web_tool_data/contents/"


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
            'grids/gridWide_g5.nc': 'md5:2706c47cc29de738bb173f064f87e42a',
            'grids/gridWide_g12.nc': 'md5:0131b839eeab315756c293e623497995',
            'model_fits/obs/GEV_covaraite_fit_HadUK_tasmax_linear_loc_log_scale_nFits_1000_parametric_False.nc': 'md5:033f678605cb3789447563a3a236745b',
            'model_fits/obs/smoothed_GEV_covaraite_fit_HadUK_1day_precip_max_log_loc_scale_nFits_1000_parametric_False.nc': 'md5:84b9a3a5ed811e40c4f311c1cdf0a771',
            'model_fits/obs/smoothed_GEV_covaraite_fit_HadUK_3day_precip_max_log_loc_scale_nFits_1000_parametric_False.nc': 'md5:a5b92853a78a81f34cd7545e47e717f3',
            'model_fits/sim/GEV_covaraite_fit_UKCP18_tasmax_linear_loc_log_scale_nFits_1000_parametric_False.nc': 'md5:a5a1713ded39b694367cebebc9748c2d',
            'model_fits/sim/smoothed_GEV_covaraite_fit_UKCP18_1day_precip_max_log_loc_scale_nFits_1000_parametric_False.nc': 'md5:3219480e3e33312756a377943d45c4fd',
            'model_fits/sim/smoothed_GEV_covaraite_fit_UKCP18_3day_precip_max_log_loc_scale_nFits_1000_parametric_False.nc': 'md5:fe369cd03c4f945ad21df25f658c0404',
        },
    )

def get_pooch(app):
    '''Get the pooch object in the context of a Flask app'''
    if not 'pooch' in g:
        g.pooch = make_pooch(path=app.config['DATA_DIR'])
    return g.pooch


def from_github_repo():
    '''A custom Pooch downloader to fetch files using the github API'''
    def _downloader(url, output_file, mypooch):
        r = requests.get(url + f'?ref={DATA_REPO_VERSION}')
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
        #downloader=from_github_repo()
    )


def init_data(app):
    '''Ensure each data file is downloaded'''
    for file in get_pooch(app).registry:
        fetch_file(file)
