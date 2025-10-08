# Climate Scenario Web Tool

This is the repository for the web component of the Scottish Climate Scenario
Decision-Making Web-Tool.

## Overview

The code is under active development and significant changes are likely,
however the main components and their interactions are shown in the diagram below.

![Architecture Diagram](docs/architecture.svg)

The main components is a [Flask][flask] web app with the following supporting elements:

 * JavaScript to handle the interactive parts of the map in the users browser.
 * Third party (Open Street Maps or Ordinance Survey) to serve the tile layer.

There is currently no separate caching or database service, but they might be used
in the future.


The server component uses the [Flask][flask]
web application framework.
Flask has an excellent [tutorial](https://flask.palletsprojects.com/en/stable/tutorial/)
that describe the concepts and layout of a typical Flask app.

The browser component relies heavily on [OpenLayers][open-layers]
to show the interactive map.
OpenLayers provide several learning resources including
[tutorials](https://openlayers.org/doc/tutorials/),
a [workshop](https://openlayers.org/workshop/en/) and
an extensive set of [examples](https://openlayers.org/en/latest/examples/).

### Typical user interaction

The typical user interaction with the web app is summarised in the sequence diagram below:

<p align="center""> <img src="docs/main_sequence.svg" width="50%"> </p>

#### Render `map.html`

The Flask app calls the `index` function ([`scotclimpact/routes.py`](scotclimpact/routes.py)) which in turn
renders the [`scotclimpact/templates/map.html`](scotclimpact/templates/map.html) template.
The templates includes an additional request for [`scotclimpact/static/src/main.js`](scotclimpact/static/src/main.js).

#### Select dataset on user input

The logic in [`scotclimpact/static/src/main.js`](scotclimpact/static/src/main.js) does several things:

  * Record the values of the drop down menus and slider positions. Default values are 
    used when the page is first loaded.
  * Hide sliders that are not relevant to the current selection in drop down menus.
  * Make an additional request to the server to calculate the dataset associated with
    the values of UI elements. 

The request is sent to a URL endpoint that is constructed based on the following template:
```
/<hazard>/<what_do_you_want_to_know>/<slider1>/<slider2>/...
```

#### Calculate hazard dataset

The web app calls a function in [`scotclimpact/routes.py`](scotclimpact/routes.py)
that corresponds to the request for the data set.

The statistical calculation is done in [`scotclimpact/extreme_temp.py`](scotclimpact/extreme_temp.py) 
(other hazards to follow).
The calculation relies heavily on the Python [xarray][xarray] package.
However, it is not possible to transfer Xarray `DataSet` objects back to the browser.
Utility functions in [`scotclimpact/data_helpers.py`](scotclimpact/data_helpers.py) are
used to convert the xarray object to GeoJSON which can be interpreted in the browser.

#### Update the Map

The 'data layer' of the map is updated. This makes heavy use of [OpenLayers][open-layers] and 
[`scotclimpact/static/src/map.js`](scotclimpact/static/src/map.js).
The legend for the relevant dataset is also updated based on a description of the dataset
in [`scotclimpact/static/src/main.js`](scotclimpact/static/src/main.js)
and logic in 
[`scotclimpact/static/src/color_map.js`](scotclimpact/static/src/color_map.js)
and
[`scotclimpact/static/src/legend.js`](scotclimpact/static/src/legend.js).

### Project directory layout

Flask recommends a directory layout for web apps in the [tutorial](https://flask.palletsprojects.com/en/stable/tutorial/layout/) 
and this project follows their convention.
A brief descriptions of some of the project files are given in the following table:

| File                                    | Description                                                                                             |
|-----------------------------------------|---------------------------------------------------------------------------------------------------------|
| `pyproject.toml`                        | Python [package][flask-tut-install] configuration. Managed with [`uv`][uv-project].                     |
| `Dockerfile`                            | Recipe to create the app's Docker container.                                                            |
| `scotclimpact/`                         | The main Python package that contain the Flask app.                                                     |
| `scotclimpact/__init__.py`              | Initialization for the python package and Flask [`app` object][flask-tut-app].                          |
| `scotclimpact/config.py`                | The app's configuration object.                                                                         |
| `scotclimpact/routes.py`                | Definition and logic for HTTP endpoints.                                                                |
| `scotclimpact/extreme_temp.py`          | Statistical calculations for extreme heat hazards.                                                      |
| `scotclimpact/wsgi.py`                  | Entry point for WSGI servers like [gunicorn][gunicorn].                                                 |
| `scotclimpact/cache.py`                 | Wrapper for the Flask-cache plugin; used to cache HTTP requests in [routes.py](scotclimpact/routes.py). |
| `scotclimpact/data.py`                  | Wrapper for the [Pooch][pooch] library; used to download [project data][data-reo].                      |
| `scotclimpact/data_helpers.py`          | Utilities to validate and transform data structures.                                                    |
| `scotclimpact/boundary_layer.py`        | Utilities to serve regional boundary data.                                                              |
| `scotclimpact/db.py`                    | Utilities to initialise and populate the [database][flask-tut-db] (unused).                             |
| `scotclimpact/schema.sql`               | Database schema (unused)                                                                                |
| `tests/`                                | Python unit tests                                                                                       |
| `scotclimpact/pages/`                   | Content for pages containing mostly textual content                                                     |
| `scotclimpact/templates/`               | HTML Jinja2 [templates][flask-tut-templates].                                                           |
| `scotclimpact/static/`                  | Content that needs to be accessible from [the browser][flask-tut-static].                               |
|                                         | Mostly JavaScript code managed as an NPM project.                                                       |
| `scotclimpact/static/package.json`      | NPM project configuration.                                                                              |
| `scotclimpact/static/webpack.config.js` | Webpack transpiler configuration.                                                                       |
| `scotclimpact/static/src/`              | JavaScript source code.                                                                                 |
| `scotclimpact/static/src/main.js`       | The main control logic for the map and UI elements on the main page.                                    |
| `scotclimpact/static/src/map.js`        | Class to wrap the [OpenLayers][open-layers] logic for the interactive map.                              |
| `scotclimpact/static/src/legend.js`     | Utilities to draw the legend.                                                                           |
| `scotclimpact/static/src/color_map.js`  | Utilities to calculate color values for the data shown on the map.                                      |
| `scotclimpact/static/src/disclaimer.js` | Logic to check that the disclaimer has been accepted.                                                   |
| `scotclimpact/static/tests/`            | JavaScript unit tests.                                                                                  |

### Data

The project's data is kept  in a [separate repository][data-repo] and automatically downloaded when the 
app is run.
The default download location is in `~/.cache/scotclimpact`.
Details of how to allow access to download the data is discussed in later sections.

## Development



There are quite a few steps needed to setup a working development environment, however
they are mostly automated in the [`run_dev.sh`](run_dev.sh) script.
The following steps are needed to get up and running using the script:

  * [Software](#software)
  * [Initial setup](#initial-setup)
    * [Code](#code)
    * [Data](#data)
    * [Using the `run_dev.sh` script](#using-the-run_devsh-script)
    * [The `PATH` variable](#the-path-variable)
  * [New Sessions](#new-sessions)
  * [Run the latest code](#run-the-latest-code)
    
The build environment can be setup manually without using the `run_dev.sh` script.
This method is outlined in the following sections and a few alternatives to handle 
Python dependencies are discussed too.
    
> [!NOTE]
> The following steps are optional and only recommended if the `run_dev.sh` script is
> is not suitable for your workflow and/or system.

  * [Additional Software](#additional-software)
    * [Install NPM](#install-npm)
    * [Install UV](#install-uv)
    * [Install Conda](#install-conda)
  * [Extra Initial Setup](#extra-initial-setup)
    * [Setup a Python virtual environment](#setup-a-python-virtual-environment)
      * [UV](#uv)
      * [Python venv/virtualenv](#python-venvvirtualenv)
      * [Conda](#conda)
    * [Initialise the NPM project](#initialise-the-npm-project)
    * [Run the web app locally](#run-the-web-app-locally)
  * [New Sessions 2](#new-sessions-2)
  * [Working on the code](#working-on-the-code)
    * [Python](#python)
    * [JavaScript](#javascript)
    * [Running the latest code](#running-the-latest-code)

### Software

A few common Linux utilities must be installed from the distribution repositories.
These include `git`, `tar`, `wget` and `curl`.

### Initial setup

The initial setup involves getting the source code and data for the
project and installing Python and JavaScript libraries needed to
run the web app.

The following steps need to be performed once.

#### Code

Clone the Git repository:
```bash
git clone https://github.com/SCSDMWT/climate_scenario_web_tool
cd climate_scenario_web_tool
```

#### Data

The project's data is held in a separate [GitHub repository][data-repo] and
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
#!/bin/bash

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

#### Using the `run_dev.sh` script

The `run_dev.sh` script will download recent versions of the package managers
(UV for Python and NPM for JavaScript) if they are not present
and download all additional software dependencies.

#### The `PATH` variable

The `PATH` variable can be set so that your terminal will use the same version of the package
managers as the `run_dev.sh` script. This can be done with
```bash
./run_dev.sh --print-export >> env_vars
. env_vars
```

### New sessions

The various environment variables needed to run the web app are only set temporarily
for the duration of a terminal session.

When starting a new terminal the `env_vars` file should also be sourced again:
```bash
cd climate_scenario_web_tool
. env_vars
```

### Run the latest code

The `run_dev.sh` script will also compile the latest changes to JavaScript code and run the
web app in developer mode.

Latest changes to the code can be run with:
```bash
./run_dev.sh
```
The script has a few additional features to override the versions and download location of 
the package managers. Run `./run_dev.sh -h` for details.

> [!NOTE]
> You should now be able to make changes to the code and run it with the `run_dev.sh` script.
> The rest of the section covers alternative ways to manage Python and JavaScript dependencies 
> and installing the required tools manually.


### Additional Software
#### Install NPM

NPM can be installed without root access with the following steps:

 * Go to [nodejs.org/en/download/](https://nodejs.org/en/download/). 
 * Selected the latest version from the first drop down
 * Click the green 'Standalone Binary (.xz)' button
 * Extract the tarball
 * Add the `bin` directory to the `PATH` variable:
   ```bash
   export PATH=/full/path/to/node/bin:$PATH
   ```


#### Install UV

UV can be installed without root privileges by following the instructions
at [docs.astral.sh](https://docs.astral.sh/uv/getting-started/installation/).

#### Install Conda

Follow the installation instructions on the [conda web site](https://docs.conda.io/projects/conda/en/stable/user-guide/install/linux.html).


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

### New sessions 2

In addition to sourcing `env_vars`, conda or virtual environments should be reactivated 
in new terminal sessions. If using conda:
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

#### Running the latest code

Running the web app with the latest changes is the same as [run the web app locally](#run-the-web-app-locally) above.


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

[flask]: https://flask.palletsprojects.com/en/stable/
[flask-tut-static]: https://flask.palletsprojects.com/en/stable/tutorial/static/
[flask-tut-templates]: https://flask.palletsprojects.com/en/stable/tutorial/templates/
[flask-tut-app]: https://flask.palletsprojects.com/en/stable/tutorial/factory/#the-application-factory
[flask-tut-db]: https://flask.palletsprojects.com/en/stable/tutorial/database/
[flask-tut-install]: https://flask.palletsprojects.com/en/stable/tutorial/install/
[uv-projects]: https://docs.astral.sh/uv/concepts/projects/
[data-repo]: https://github.com/SCSDMWT/climate_scenario_web_tool_data
[pooch]: https://www.fatiando.org/pooch/latest/
[gunicorn]: https://gunicorn.org/
[open-layers]: https://openlayers.org/
[xarray]: https://docs.xarray.dev/en/stable/
