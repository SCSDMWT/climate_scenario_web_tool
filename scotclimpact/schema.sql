--CREATE EXTENSION postgis;

CREATE TABLE IF NOT EXISTS model_parameters (
    id SERIAL PRIMARY KEY,
    geom geometry,
    param_a double precision
);


