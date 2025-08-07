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

### Building the Flask App Docker image

Generate a [GitHub Personal Access Token](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens)
and login to your GitHub account:
```bash
sudo docker login ghcr.io -u <gitub_username>
```

Compile the JavaScript code:
```bash
cd scotclimpact/static
npm run build
cd ../..
```
Build the Docker image:
```bash
sudo docker build -t SCSDMWT/climate_scenario_web_tool .
```
Run the app as a Docker Compose project:
```bash
cd docker
#sudo docker compose run -v $PWD/../mapserver:/app/data web flask --app scotclimpact import-nc 27700 tas /app/data/Scotland_HadUK-grid_2024_tas.nc
sudo docker compose up -d
```

Initialise and populate the database 
```bash
cd ..
wget -O mapserver/Scotland_HadUK-grid_2024_tas.nc "https://www.geos.ed.ac.uk/~ddekler/Scotland_HadUK-grid_2024_tas.nc"
uv run -- flask --app scotclimpact init-db
uv run -- flask --app scotclimpact import-nc 27700 tas mapserver/Scotland_HadUK-grid_2024_tas.nc
```

The latest version of the web tool should be running in [http://localhost](http://localhost).

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

### Javascript

Javascript dependencies are managed in an `npm` project in `scotclimpact/static`.
Changes to `scotclimpact/static/src/` should be compiled with
```bash
cd scotclimpact/static
npm run build
```

## Licence

See [LICENCE](LICENCE).
