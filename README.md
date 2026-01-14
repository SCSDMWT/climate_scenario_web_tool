# Climate Scenario Web Tool

This is the repository for the web component of the Scottish Climate Scenario
Decision-Making Web-Tool.

> [!IMPORTANT]
> The web tool is under active development and significant changes are likely.

A [pre-production](https://www.geos.ed.ac.uk/dev/ddekler/) version of the Web Tool is
served by the [School of GeoSciences](https://geosciences.ed.ac.uk/)

## Overview

The main components of the web tool and their interactions are shown in the diagram below.

![Architecture Diagram](docs/architecture.svg)

The main components is a [Flask][flask] web app with the following supporting elements:

 * JavaScript to handle the interactive parts of the map in the users browser.
 * Third party (Open Street Maps or Ordinance Survey) to serve the tile layer.
 * PostgreSQL database to store pre-computed hazard data. If the database is not present,
   hazard data will be calculated per request.

There is currently no separate caching, but it might be used in the future.


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

Each step in the process is described in a bit more detail below.

#### Render `map.html`

The Flask app calls the `index` function (defined in [`scotclimpact/routes.py`](scotclimpact/routes.py)) which
in turn renders the [`scotclimpact/templates/map.html`](scotclimpact/templates/map.html) template.
The templates includes an additional request for [`scotclimpact/static/src/main.js`](scotclimpact/static/src/main.js).

#### Select dataset on user input

The logic in [`scotclimpact/static/src/main.js`](scotclimpact/static/src/main.js) runs in the browser and
does several things:

  * Request a list of hazards from the server and populate the sliders, drop down menus,
    descriptions and legend.
  * Record the values of the UI elements.  
  * Make an additional request to the server to calculate the dataset associated with
    the values of UI elements.

The request is sent to a URL endpoint that is constructed based on the following template:
```
/map/data/<hazard>_<calculation>?param1=value1&...
```

#### Calculate hazard dataset

The web app calls the `data` function in [`scotclimpact/routes.py`](scotclimpact/routes.py)
with the hazard selected by the user.

The statistical calculation is done in [`scotclimpact/developing_process.py`](scotclimpact/developing_process.py).
The calculation relies heavily on the Python [Xarray][xarray] package.
However, it is not possible to transfer Xarray `DataSet` objects back to the browser.
Utility functions in [`scotclimpact/data_helpers.py`](scotclimpact/data_helpers.py) are
used to convert the Xarray object to GeoJSON which can be transferred to and interpreted in the browser.

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
A brief descriptions of some of the project files are given in the following:

<big><pre>
**climate\_scenario\_web\_tool**/
├─ pyproject.toml              Python [package][flask-tut-install] configuration. Managed as a [`uv`][uv-projects] project.
├─ Dockerfile                  Recipe to create the app's Docker container.
├─ run_dev.sh                  A script that runs the web tool in developer mode.
├─ **scotclimpact**/               The main Python package that contain the Flask app.
│  ├─ \_\_init\_\_.py              Initialization for the python package and Flask [`app` object][flask-tut-app].
│  ├─  config.py               The app's configuration object.
│  ├─  routes.py               Definition and logic for HTTP endpoints.
│  ├─  developing_process.py   Statistical calculations for extreme heat hazards.
│  ├─  hazards.py              A data structure containing metadata for all available hazards.
│  ├─  wsgi.py                 Entry point for WSGI servers like [gunicorn][gunicorn].
│  ├─  cache.py                Wrapper for the Flask-cache plugin; used to cache HTTP requests in [routes.py](scotclimpact/routes.py).
│  ├─  data.py                 Wrapper for the [Pooch][pooch] library; used to download [project data][data-repo].
│  ├─  data_helpers.py         Utilities to validate and transform data structures.
│  ├─  boundary_layer.py       Utilities to serve regional boundary data.
│  ├─  db.py                   Utilities to initialise and populate the [database][flask-tut-db].
│  ├─  schema.sql              Database schema (unused)
│  ├─  **pages**/                  Content for pages containing mostly textual content
│  ├─  **templates**/              HTML Jinja2 [templates][flask-tut-templates].
│  └─  **static**/                 Content that needs to be accessible from [the browser][flask-tut-static]. Mostly JavaScript code managed as an [npm][npm-intro] project.
│      ├─  package.json        npm project configuration.
│      ├─  webpack.config.js   Webpack transpiler configuration.
│      ├─  **src**/                JavaScript source code.
│      │   ├─  main.js         The main control logic for the map and UI elements on the main page.
│      │   ├─  map.js          Class to wrap the [OpenLayers][open-layers] logic for the interactive map.
│      │   ├─  legend.js       Utilities to draw the legend.
│      │   ├─  color_map.js    Utilities to calculate color values for the data shown on the map.
│      │   ├─  slider.js       Utilities to create the slider UI elements.
│      │   └─  disclaimer.js   Logic to check that the disclaimer has been accepted.
│      └─  **tests**/              JavaScript unit tests.
└─ **tests**/                      Python unit tests
</pre></big>

### Data

The project's data is kept  in a [separate repository][data-repo] and automatically downloaded when the
app is run.
The default download location is `~/.cache/scotclimpact`.
Details of how to allow access to download the data is discussed in later sections.

The statistical calculation uses datasets in [NetCDF][netcdf] format. The [Xarray][xarray] library
is used to read and manipulate the datasets.

Region boundaries are kept in GeoJSON format. These are large text files that are essentially read
send to the browser when requested.

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
    * [Other environment variables](#other-environment-variables)
  * [New Sessions](#new-sessions)
  * [Run the latest code](#run-the-latest-code)

The build environment can be setup manually without using the `run_dev.sh` script and
is outlined [elsewhere in the documentation](docs/alternative_dev_setup.md).

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
git clone git@github.com/SCSDMWT/climate_scenario_web_tool.git
cd climate_scenario_web_tool
```

#### Data

The project's data is held in a separate [GitHub repository][data-repo] and
automatically downloaded when needed.

#### Using the `run_dev.sh` script

The `run_dev.sh` script will download recent versions of the package managers
(uv for Python and npm for JavaScript) if they are not present
and download all additional software dependencies.

#### The `PATH` variable

The `PATH` variable can be set so that your terminal will use the same version of the package
managers as the `run_dev.sh` script. This can be done with
```bash
echo "#!/bin/bash" > env_vars
./run_dev.sh --print-export >> env_vars
. env_vars
```

#### Other environment variables

The app can be configured using several environment variables which
are defined in [`scotclimpact/config.py`](scotclimpact/config.py).
If you want to set any of these, adding relevant `export` commands in `env_vars` is
the best place to do so.

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


## Running with Docker

Running with [Docker](https://www.docker.com/) is the recommended way to serve the web app on a server.
A basic version of the web tool can be run with Docker using the following:
```bash
docker pull ghcr.io/scsdmwt/climate_scenario_web_tool:latest
sudo docker run \
    -e DATA_DIR=/app/data \
    -p 80:80 \
    -t ghcr.io/scsdmwt/climate_scenario_web_tool:latest
```

An example of running the web tool with it's database in separate containers is given in [docker/docker-compose.yml](docker/docker-compose.yml).

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
[netcdf]: https://www.unidata.ucar.edu/software/netcdf
[npm-intro]: https://nodejs.org/en/learn/getting-started/an-introduction-to-the-npm-package-manager
