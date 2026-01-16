from flask import g, current_app
import pooch
import requests

DATA_REPO_VERSION = "v0.1.0"
GITHUB_API_URL = "https://media.githubusercontent.com/media/SCSDMWT/climate_scenario_web_tool_data/{version}"

'''
Meta-data that describes which hazards use which datafiles etc.
'''
datasets = dict(
    extreme_temp=dict(
        model_file='GEV_covaraite_fit_%s_tasmax_linear_loc_log_scale_nFits_1000_parametric_False.nc',
        grid_size=12,
        grid_selection=dict(
            projection_x_coordinate = slice(0,0.5e6),
            projection_y_coordinate = slice(0.46e6,1.21e6),
        ),
    ),
    sustained_3day_Tmin_intensity=dict(
        model_file='exclude_GEV_covaraite_fit_%s_max_3day_tasmin_linear_loc_log_scale_nFits_1000_parametric_False.nc',
        grid_size=12,
        grid_selection=dict(
            projection_x_coordinate = slice(0,0.5e6),
            projection_y_coordinate = slice(0.46e6,1.21e6),
        ),
    ),
    extreme_1day_precip=dict(
        model_file='smoothed_GEV_covaraite_fit_%s_1day_precip_max_log_loc_scale_nFits_1000_parametric_False.nc',
        grid_size=5,
        grid_selection=dict(
            projection_x_coordinate=slice(0,0.5e6),
            projection_y_coordinate=slice(0.46e6,1.1e6),
        ),
    ),
    extreme_3day_precip=dict(
        model_file='smoothed_GEV_covaraite_fit_%s_3day_precip_max_log_loc_scale_nFits_1000_parametric_False.nc',
        grid_size=5,
        grid_selection=dict(
            projection_x_coordinate=slice(0,0.5e6),
            projection_y_coordinate=slice(0.46e6,1.1e6),
        ),
    ),
)

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
            'model_fits/obs/exclude_GEV_covaraite_fit_HadUK_max_3day_tasmin_linear_loc_log_scale_nFits_1000_parametric_False.nc': 'md5:4ab28431bc9e005ac1ddef92b4bcdb7d',
            'model_fits/sim/GEV_covaraite_fit_UKCP18_tasmax_linear_loc_log_scale_nFits_1000_parametric_False.nc': 'md5:a5a1713ded39b694367cebebc9748c2d',
            'model_fits/sim/smoothed_GEV_covaraite_fit_UKCP18_1day_precip_max_log_loc_scale_nFits_1000_parametric_False.nc': 'md5:3219480e3e33312756a377943d45c4fd',
            'model_fits/sim/smoothed_GEV_covaraite_fit_UKCP18_3day_precip_max_log_loc_scale_nFits_1000_parametric_False.nc': 'md5:fe369cd03c4f945ad21df25f658c0404',
            'model_fits/sim/exclude_GEV_covaraite_fit_UKCP18_max_3day_tasmin_linear_loc_log_scale_nFits_1000_parametric_False.nc': 'md5:5507fba4c2f0ebb6ffdb43bf97b688be',
        },
    )

def get_pooch(app):
    '''Get the pooch object in the context of a Flask app'''
    if not 'pooch' in g:
        g.pooch = make_pooch(path=app.config['DATA_DIR'])
    return g.pooch


def fetch_file(filename):
    '''Downloads a file in the registry and returns it's local filename.'''
    pooch_ = get_pooch(current_app)
    return pooch_.fetch(
        filename, 
    )


def init_data(app):
    '''Ensure each data file is downloaded'''
    for file in get_pooch(app).registry:
        fetch_file(file)
