#!/bin/bash

## Load possible scripts containing environment variables
if [ -f .dev-env ]; then
    source .dev-env
fi

if [ -f env_vars ]; then
    source env_vars
fi

## Compile the JavaScript code
cd scotclimpact/static
npm install || exit 1
npm run build || exit 1
cd -

## Run the Flask app
uv run -- flask --app scotclimpact run -p 8000
