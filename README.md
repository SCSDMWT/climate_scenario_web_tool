# ScotClImpact

## Dev

Using [`uv`](https://docs.astral.sh/uv) for managing dependancies as recommended.

Setup containers:
```bash
sudo docker compose up
```

Initialise the database:
```bash
uv run -- flask --app scotclimpact init-db
```

Run the the web app locally:
```bash
uv run -- flask --app scotclimpact run -p 8000
```

