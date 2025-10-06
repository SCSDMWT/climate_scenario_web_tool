# Climate Scenario Web Tool

This is the repository for the web component of the Scottish Climate Scenario 
Decision-Making Web-Tool.

The code is under active development and significant changes are likely, 
however the main components and their interactions are shown in the diagram below.

![Archetecture Diagram](docs/architecture.svg)

The main components is a Flask web app with the following supporting elements:

 * JavaScript to handle the interactive parts of the map in the users browser.
 * Third party (Open Street Maps or Ordinance Survey) to serve the tile layer.

There is currently no separate caching or database service, but they might be used
in the future.

## Development

### Software

Making changes to the code will require a Linux machine and 
the following software:

 * [git](https://git-scm.com) -- Source code version control
 * [npm](https://www.npmjs.com/) -- JavaScript package manager
 * [uv](https://docs.astral.sh/uv)  -- A Python package manager (Optional and recommended) 
 * [conda]()  -- A package manager (Optional, if uv is not available and system installation of Python is older than 3.13) 

#### Installing Git

It is best [installed](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git) via 
the package manager of the Linux distribution.

#### Installing NPM

On Ubuntu systems with root access, run
```bash
sudo apt-get install npm
```

NPM can be installed without root access by following the instructions 
at [nodejs.org/en/download/](https://nodejs.org/en/download/).

#### Install UV

UV can be installed without root prevelages by following the instructions 
at [docs.astral.sh](https://docs.astral.sh/uv/getting-started/installation/).

### Setup

The following steps need to be performed once.

#### Code

Clone the Git repository:
```bash
git clone https://github.com/SCSDMWT/climate_scenario_web_tool
cd climate_scenario_web_tool
```

#### Data

Data is held in a separate [GitHub repository](https://github.com/SCSDMWT/climate_scenario_web_tool_data) and
automatically downloaded when needed.

For the web app to access the data a [Fine Grained tokeni](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens)
has to be generated with

 * the Resource owner set to SCSDMWT
 * Only Select repositories and pick SCSDMWT/climate_scenario_web_tool_data
 * Under add permissions pick Contents.
   
The token should be held in an environment variable called `DATA_REPO_GITHUB_TOKEN`, however
care should be taken not to accedentally store the token in the shell's history.

Create a file called `env_vars` with the following content (replacing `...` with the value of the token):
```bash
export DATA_REPO_GITHUB_TOKEN=...
```
It is good practice to restrict the file's permissions by running
```bash
chmod 600 env_vars
```
The environment variable can now be set by running:
```bash
. env_vars
```

#### Setup a Python virtual environment

It is recommended to keep the Python dependancies for the project in a separate environment.
This can be done with (atleast) three software packages.

##### UV

UV creates temporary envirnments whenever a Python script or program is run using `uv run`.
If `uv` is installed, no additional setup is needed at this stage.

##### Python venv/virtualenv

```bash
python -m venv .venv
. .venv/bin/activate
pip install .
```

##### Conda

```bash
conda create -n scotclimpact python=3.13.0
conda activate scotclimpact
pip install .
```


#### Initialise the NPM project

JavaScript dependancies need to be downloaded and installed with:
```bash
cd scotclimpact/static
npm install
cd -
```

#### Run the webapp locally

When using UV, the following command will download all Python dependancies and run the web app:
```bash
uv run -- flask --app scotclimpact run -p 8000
```

With conda and a virtual environment, the same can be done with:
```bash
flask --app scotclimpact run -p 8000
```

Local changes to the code should be running in [http://localhost:8000](http://localhost:8000).

### New sessions

When starting a new terminal, conda or virtual environments should be reactivated. 
The `env_vars` file should also be sourced again:
```bash
cd climate_scenario_web_tool
. env_vars
```
If using conda:
```bash
conda activate scotclimpact
```
If using venv/virtualenv:
```bash
. .venv/bin/activate
```

### Working on the code

Changes to the Python code might require additional steps, depending on how the Python environment
is managed. Changes to the JavaScript code should be recompiled too.

#### Python

With UV no extra steps are needed, but conda and virtual environments might need the following to 
install the updated code in the environment:
```
pip install .
```

#### JavaScript

Changes to `scotclimpact/static/src/` should be compiled with
```bash
cd scotclimpact/static
npm run build
cd -
```

## Running with Docker

Running with [Docker](https://www.docker.com/) is the recommended way to serve the web app on a server. 
This method requires two slightly different authentication methods to 
download the data from the data repository (see the Data section above) and
to download the container. 

Generate a Personal Access Token (classic) and make sure to tick 'read:packages'. 
Save the access token in the `GITHUB_PAT` environment variable.

Login with docker (assuming the access token is the value of the environment variable `GITHUB_PAT`), pull the image and run:
```bash
echo $GITHUB_PAT | docker login ghcr.io -u USERNAME --password-stdin
docker pull ghcr.io/scsdmwt/climate_scenario_web_tool:latest
sudo docker run \
    -e DATA_REPO_GITHUB_TOKEN=$DATA_REPO_GITHUB_TOKEN \
    -e DATA_DIR=/app/data \
    -v ~/.cache/scotclimpact:/app/data \
    -p 80:80 \
    -t ghcr.io/scsdmwt/climate_scenario_web_tool:latest
```

## Licence

See [LICENCE](LICENCE).
