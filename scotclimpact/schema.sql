--CREATE EXTENSION postgis;

CREATE TABLE IF NOT EXISTS model_parameters (
    id SERIAL PRIMARY KEY,
    geom GEOMETRY,
    param_a DOUBLE PRECISION,
    source VARCHAR,
    CONSTRAINT unique_source UNIQUE (source)
);


