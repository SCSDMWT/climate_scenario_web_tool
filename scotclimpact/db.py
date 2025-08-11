import click
from flask import current_app, g
import numpy as np
import psycopg2
import xarray as xr


def get_db():
    """Returns the current connection object to the Postgre database."""
    if not 'db' in g:
        g.db = psycopg2.connect(current_app.config["DATABASE_URL"])
    return g.db

def close_db(e=None):
    """Close the current connection to the database."""
    db = g.pop('db', None)
    if db is not None:
        db.close()


def init_db():
    """Runs the database schema against a potentialy un-initialised database."""
    db = get_db()
    with current_app.open_resource("schema.sql") as f:
        with db.cursor() as cursor:
            cursor.execute(f.read().decode("utf8"))
    db.commit()


@click.command("init-db", short_help="Initialise the database")
def init_db_cli():
    """Command line wrapper for init_db"""
    click.echo("Init DB")
    init_db()


@click.command("import-nc")
@click.option("--slice", default=0)
@click.argument("projection", type=str)
@click.argument("variable", type=str)
@click.argument("filename", type=click.File("r"))
def import_nc4(projection, variable, filename, slice=0):
    """Commandline function to import NetCDF FILENAME into the database.
    """
    click.echo(f"Importing: {filename.name} in EPSG:{projection}")

    ds = xr.open_dataset(filename.name)

    x_dim = ds['projection_x_coordinate'].to_numpy()
    y_dim = ds['projection_y_coordinate'].to_numpy()


    # Load the data
    dataset = ds[variable].to_numpy()
    idx = np.where(dataset[slice] == dataset[slice])

    # Find existing data
    db = get_db()
    with db.cursor() as cursor:
        cursor.execute("SELECT source FROM model_parameters")
        existing_source = {item[0] for item in cursor.fetchall()}
    new_source = [
        f"{filename.name}:{variable}:{slice}:{x}:{y}"
        for x,y in zip(*idx)
    ]

    # Map edges to EPSG:4326 (lat/long)
    #transform = Transformer.from_crs(f"EPSG:{projection}", "EPSG:3875")
    #transform = Transformer.from_crs(f"EPSG:{projection}", "EPSG:4326")
    dx = np.diff(x_dim).mean()/2.0
    dy = np.diff(y_dim).mean()/2.0
    def transform_to_sql_format(x, y):
        #a, b = transform.transform(x, y)
        return f"{x} {y}"
    top_right =    [ transform_to_sql_format(x_dim[i]+dx, y_dim[j]+dy) for j, i in zip(*idx)]
    top_left  =    [ transform_to_sql_format(x_dim[i]+dx, y_dim[j]-dy) for j, i in zip(*idx) ]
    bottom_right = [ transform_to_sql_format(x_dim[i]-dx, y_dim[j]+dy) for j, i in zip(*idx) ]
    bottom_left  = [ transform_to_sql_format(x_dim[i]-dx, y_dim[j]-dy) for j, i in zip(*idx) ]

    # Create the SQL query
    values = [
        (f"('POLYGON (({tr}, {tl}, {bl}, {br}, {tr}))'," +
         f"{v}," +
         f"'{s}'" +
         ")"
         )
        for s, tr, tl, br, bl, v in zip(new_source, top_right, top_left, bottom_right, bottom_left, dataset[slice][idx])
        if not s in existing_source
    ]

    if len(values) == 0:
        return
    values_clause = ','.join(values)
    query = f"INSERT INTO model_parameters (geom, param_a, source) VALUES {values_clause};"

    # Run the query
    with db.cursor() as cursor:
        cursor.execute(query)
    db.commit()


def init_app(app):
    """Register database functions with the Flask application."""
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_cli)
    app.cli.add_command(import_nc4)
