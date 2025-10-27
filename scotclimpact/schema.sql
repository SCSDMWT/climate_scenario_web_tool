--CREATE EXTENSION postgis;

CREATE TABLE IF NOT EXISTS hazard_data (

    id SERIAL PRIMARY KEY,
    -- 
    geom GEOMETRY,
    x_idx INT,
    y_idx INT,
    --
    function TEXT,
    -- Function parameters
    covariate DOUBLE PRECISION,
    return_time INT,
    intensity INT,
    covariate_comp DOUBLE PRECISION,
    -- Results
    central_estimate DOUBLE PRECISION,
    ci_report TEXT
);

CREATE INDEX IF NOT EXISTS hazard_data_lookup ON hazard_data (function, covariate, return_time, intensity, covariate_comp);
