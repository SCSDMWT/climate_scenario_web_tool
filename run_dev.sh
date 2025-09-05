#!/bin/bash

if [ -f .dev-env ]; then
    source .dev-env
fi

cd scotclimpact/static
npm install
npm run build
cd -

uv run -- flask --app scotclimpact run -p 8000
