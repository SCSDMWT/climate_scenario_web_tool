# Climate Scenario Web Tool

This is the repository for the web component of the Scottish Climate Scenario 
Decision-Making Web-Tool.

The code is under active development and significant changes are likely, 
however the main components and their interactions are shown in the diagram below.

![Archetecture Diagram](docs/architecture.svg)

The main components is a Flask web app with the following supporting elements:

 * JavaScript to handle the interactive parts of the map in the users browser.
 * A command line tool to initialise a database
 * Mapserver to serve GIS data for the interactive data layer
 * Third party (Open Street Maps or Ordinance Survey) to serve the tile layer.

## Development

Making changes to the code will require a Linux machine with root privileges and 
the following software:

 * [git](https://git-scm.com) -- Source code version control
 * [uv](https://docs.astral.sh/uv) -- A Python package manager
 * [npm](https://www.npmjs.com/) -- JavaScript package manager
 * [Docker](https://www.docker.com/) and [Docker compose](https://www.docker.com/) 
   -- to run local instances of Mapserver and Postgres

Get the code:
```bash
git clone https://github.com/SCSDMWT/climate_scenario_web_tool
cd climate_scenario_web_tool
```

### Data

The input data (all `.nc` files) should be downloaded and copied into the project root directory from
the [prototype plotting tool](https://github.com/SCSDMWT/prototype_tool_plotting).

### Javascript

Javascript dependencies are managed in an `npm` project in `scotclimpact/static`.
Changes to `scotclimpact/static/src/` should be compiled with
```bash
cd scotclimpact/static
npm run build
```

### Python

Changes to the Python code can be ran without re-building the Docker container.
 
It is recommended to use [`uv`](https://docs.astral.sh/uv) to setup the Python environment for the web app.
Create a virtual environment with:
```bash
uv venv
. .venv/bin/activate
```

Run the the web app locally:
```bash
uv run -- flask --app scotclimpact run -p 8000
```

Local changes to the code should be running in [http://localhost:8000](http://localhost:8000).

## Licence

See [LICENCE](LICENCE).
