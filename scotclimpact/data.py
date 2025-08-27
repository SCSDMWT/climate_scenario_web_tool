from flask import g, current_app
import pooch
import requests

DATA_REPO_VERSION = "v0.0.2"
GITHUB_API_URL = "https://api.github.com/repos/SCSDMWT/climate_scenario_web_tool_data/contents/"

def get_pooch(app):
    if not 'pooch' in g:
        g.pooch = pooch.create(
            path=app.config['DATA_DIR'],
            base_url=GITHUB_API_URL,
            version=DATA_REPO_VERSION,
            version_dev="main",
            registry={
                'boundaries/fire_rescue.json': 'md5:4fcfc1910ff0b14ff1a151539eb47fcb',
                'boundaries/health_boards.json': 'md5:c8d78c5ae40e9f2cd923f20011e4965c',
                'boundaries/health_integration_authorities.json': 'md5:ce33d6a6d1e48f856388e0a8bbbf3e9a',
                'boundaries/local_authorities.json': 'md5:5e0a3d394e402ffb52c5e9124ac359ab',
                'boundaries/police.json': 'md5:c380d0bbe3b1e503789222e87e601594',
            },
        )
    return g.pooch


def from_private_github_repo(url, output_file, mypooch):
    '''A custom Pooch downloader to fetch files from a private github repository'''
    api_request_headers = dict(
        Authorization=f"token {current_app.config['GITHUB_TOKEN']}",
    )
    r = requests.get(url + f'?ref={DATA_REPO_VERSION}', headers=api_request_headers)
    if not r.status_code == 200:
        print(f"[{r.status_code}] {r.text}")
        return

    download_url = r.json()['download_url']
    downloader = pooch.HTTPDownloader()
    downloader(download_url, output_file, mypooch)


def fetch_file(filename):
    '''Downloads a file in the registry and returns it's local filename.'''
    pooch_ = get_pooch(current_app)
    pooch_.fetch(filename, downloader=from_private_github_repo)


def init_data(app):
    '''Ensure each data file is downloaded'''
    for file in get_pooch(app).registry:
        fetch_file(file)
