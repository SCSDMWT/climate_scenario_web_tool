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

There are quite a few steps needed to setup a working development environment. 

  * [Software](#software)
    * [Install Git](#install-git)
    * [Install NPM](#install-npm)
    * [Install UV](#install-uv)
    * [Install Conda](#install-conda)
  * [Initial setup](#initial-setup)
    * [Code](#code)
    * [Data](#data)
    * [Setup a Python virtual environment](#setup-a-python-virtual-environment)
      * [UV](#uv)
      * [Python venv/virtualenv](#python-venvvirtualenv)
      * [Conda](#conda)
    * [Initialise the NPM project](#initialise-the-npm-project)
    * [Run the web app locally](#run-the-web-app-locally)
  * [New Sessions](#new-sessions)
  * [Working on the code](#working-on-the-code)
    * [Python](#python)
    * [JavaScript](#javascript)
    

### Software

Making changes to the code will require a Linux machine and 
the following software:

 * [git](https://git-scm.com) -- Source code version control
 * [npm](https://www.npmjs.com/) -- JavaScript package manager
 * [uv](https://docs.astral.sh/uv)  -- A Python package manager (Optional and recommended) 
 * [conda]()  -- A package manager (Optional, if uv is not available and system installation of Python is older than 3.13) 

#### Install Git

It is best [installed](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git) via 
the package manager of the Linux distribution.

#### Install NPM

On Ubuntu systems with root access, run
```bash
sudo apt-get install npm
```

NPM can be installed without root access by following the instructions 
at [nodejs.org/en/download/](https://nodejs.org/en/download/).

#### Install UV

UV can be installed without root privileges by following the instructions 
at [docs.astral.sh](https://docs.astral.sh/uv/getting-started/installation/).

#### Install Conda

Follow the installation instructions on the [conda web site](https://docs.conda.io/projects/conda/en/stable/user-guide/install/linux.html).

### Initial setup

The following steps need to be performed once.

#### Code

Clone the Git repository:
```bash
git clone https://github.com/SCSDMWT/climate_scenario_web_tool
cd climate_scenario_web_tool
```

#### Data

The project's data is held in a separate [GitHub repository](https://github.com/SCSDMWT/climate_scenario_web_tool_data) and
automatically downloaded when needed.

For the web app to access the data a [Fine Grained token](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens)
has to be generated with

 * the Resource owner set to SCSDMWT
 * Only Select repositories and pick SCSDMWT/climate_scenario_web_tool_data
 * Under add permissions pick Contents.
   
The token should be held in an environment variable called `DATA_REPO_GITHUB_TOKEN`, however
care should be taken not to accidentally store the token in the shell's history.

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

It is recommended to keep the Python dependencies for the project in a separate environment.
This can be done with (at least) three software packages. 
Any one of the following three will do the job, however UV is much more convenient to use.
If UV is not available, Python venv/virtualenv should be considered before Conda environments, 
unless the system installed version of Python is too old.

##### UV

UV creates temporary environments whenever a Python script or program is run using `uv run`.
If `uv` is installed, no additional setup is needed at this stage.

##### Python venv/virtualenv

Python has a builtin mechanism for creating virtual environments, however it uses the
Python installation of the operating system. If the version is recent enough, a
virtual environment can be created with:
```bash
python -m venv .venv
. .venv/bin/activate
pip install .
```

##### Conda

Conda is a popular package manager and can install recent versions of Python without root permissions.
A conda environment can be created with:
```bash
conda create -n scotclimpact python=3.13.0
conda activate scotclimpact
pip install .
```


#### Initialise the NPM project

JavaScript dependencies need to be downloaded and the code compiled to a browser
supported format with:
```bash
cd scotclimpact/static
npm install
npm run build
cd -
```

#### Run the web app locally

When using UV, the following command will download all Python dependencies and run the web app:
```bash
uv run -- flask --app scotclimpact run -p 8000
```

With conda and a virtual environment, the web app can be started with:
```bash
flask --app scotclimpact run -p 8000
```
The web app should be running and available at [http://localhost:8000](http://localhost:8000).

### New sessions

When starting a new terminal, conda or virtual environments should be reactivated and
the `env_vars` file should also be sourced again:
```bash
cd climate_scenario_web_tool
. env_vars
```
If using conda:
```bash
conda activate scotclimpact
```
For venv/virtualenv:
```bash
. .venv/bin/activate
```

### Working on the code

Changes to the Python code might require additional steps to run, depending on how the Python environment
is managed. Changes to the JavaScript code should be recompiled too.

#### Python

With UV no extra steps are needed when changing the Python code, but conda and virtual environments 
might need the following to install the updated code in the environment:
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
