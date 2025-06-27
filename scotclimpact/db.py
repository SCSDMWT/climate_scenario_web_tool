import click
from flask import current_app, g
import numpy as np
import psycopg2
from pyhdf.SD import SD, SDC

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
@click.argument("filename", type=click.File("r"))
def import_nc4(filename):
    """Commandline function to import NetCDF FILENAME into the database."""
    click.echo(f"Importing: {filename.name}")
    breakpoint()

@click.command("import-hdfeos")
@click.argument("filename", type=click.File("r"))
def import_hdfeos(filename):
    """Commandline function to import HDF-EOS formatted FILENAME into the database."""
    click.echo(f"Importing: {filename.name}")
    hdf = SD(filename.name, SDC.READ)
    x_dim = np.linspace(3.0, 4.0, num=1200, endpoint=False)
    y_dim = np.linspace(17.0, 18.0, num=1200, endpoint=False)
    xx, yy = np.meshgrid(x_dim, y_dim)
    dataset = hdf.select("LST_Day_1km")

    idx = np.where(dataset[:] > 0)
    
    values = [
        f"('POINT({x} {y})', {v * dataset.scale_factor - 273})"
        for x, y, v in zip(xx[idx], yy[idx], dataset[:][idx])
    ]
    values_clause = ','.join(values)

    db = get_db()
    with db.cursor() as cursor:
        cursor.execute(f"INSERT INTO model_parameters (geom, param_a) VALUES {values_clause};")
    db.commit()


def init_app(app):
    """Register databese functions with the Flask application."""
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_cli)
    app.cli.add_command(import_nc4)
    app.cli.add_command(import_hdfeos)
