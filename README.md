# ScotClImpact

## Dev


### Python

The web app requires a PostgreSQL database and Mapserver.
These can be hosted with docker compose on a Linux device with root access:
[TODO]
```bash
sudo docker compose up
```

It is reccomended to use [`uv`](https://docs.astral.sh/uv) to setup the Python environment for the web app.
Create a virtual environment with:
```bash
uv venv
. .venv/bin/activate
```
TODO: Set environment variables to point to the database and Mapserver.

Initialise the database:
```bash
uv run -- flask --app scotclimpact init-db
```

TODO: Import data.

Run the the web app locally:
```bash
uv run -- flask --app scotclimpact run -p 8000
```

### Javascript

Javascript dependencies are managed in an `npm` project in `scotclimpact/static`.
Changes to `scotclimpact/static/src/` should be compiled with
```bash
cd scotclimpact/static
npm run build
```

### Building the Docker Image

 * Generate a [GitHub Personal Access Token](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens).

Build the JavaScript code:
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
uv run -- flask --app scotclimpact init-db
uv run -- flask --app scotclimpact import-nc 27700 tas  mapserver/Scotland_HadUK-grid_2024_tas.nc
```

## Licence

See [LICENCE](LICENCE).



