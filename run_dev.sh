#!/bin/bash

if [ -f .dev-env ]; then
    source .dev-env
fi

cd scotclimpact/static
npm install || exit 1
npm run build || exit 1
cd -

uv run -- flask --app scotclimpact run -p 8000
