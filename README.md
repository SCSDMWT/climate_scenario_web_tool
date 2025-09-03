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

Data is held in a separate [GitHub repository](https://github.com/SCSDMWT/climate_scenario_web_tool_data) and
automatically downloaded when needed.

For the web app to access the data a [Fine Grained tokeni](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens)
has to be generated with

 * the Resource owner set to SCSDMWT
 * Only Select repositories and pick SCSDMWT/climate_scenario_web_tool_data
 * Under add permissions pick Contents.
   
Save the token in `DATA_REPO_GITHUB_TOKEN` environment variable.

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

## Running with Docker

Running the Docker image requires two slightly different authentication methods 
download the data from the data repository (see the Data section above) and
to download the container. 

Generate a Personal Access Token (classic) and make sure to tick 'read:packages'. 
Save the access token in the `GITHUB_PAT` environment variable.

Login with docker (assuming the access token is the value of the environment variable `GITHUB_PAT`), pull the image and run:
```console
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
