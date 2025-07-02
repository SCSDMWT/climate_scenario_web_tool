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

## Licence

See [LICENCE](LICENCE).



