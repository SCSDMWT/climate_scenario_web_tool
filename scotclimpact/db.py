import click
from flask import current_app, g
import itertools
import numpy as np
#import psycopg2
#import psycopg2.pool import SimpleConnectionPool
import xarray as xr

from . import extreme_temp
from .postgres import pgdb
from .data_helpers import (sql_to_geojson, unwrapped_xarray_to_sql, unwrap_xarray)

def get_db():
    """Returns the current connection object to the Postgre database."""
    return pgdb.get_cursor()


def init_db():
    """Runs the database schema against a potentialy un-initialised database."""
    with current_app.open_resource("schema.sql") as f:
        with pgdb.get_cursor() as cursor:
            cursor.execute(f.read().decode("utf8"))


@click.command("db-init", short_help="Initialise the database")
def init_db_cli():
    """Command line wrapper for init_db"""
    click.echo("Init DB")
    init_db()



def _make_where_clause(params):
    string_type_columns = {'function', 'ci_report'};

    checks = [
        f"{column} = '{value}'" if column in string_type_columns else f"{column} = {value}"
        for column, value in params.items()
    ]

    return ' AND '.join(checks)


def has_results(**kwargs):
    if not pgdb.is_connected():
        return False
    where_clause = _make_where_clause(kwargs)
    with pgdb.get_cursor() as cursor:
        cursor.execute(f"SELECT count(id) FROM hazard_data WHERE {where_clause};")
        result = cursor.fetchall()
        return len(result) > 0


def get_json_hazard_data(**kwargs):
    where_clause = _make_where_clause(kwargs)
    with pgdb.get_cursor() as cursor:
        cursor.execute(f"SELECT central_estimate, ST_AsGeoJSON(geom), ci_report FROM hazard_data WHERE {where_clause};")
        results = cursor.fetchall()
    return sql_to_geojson(kwargs['function'], results)
    

def db_insert(query):
    '''Wrapper to run a SQL query that does not return data against the database'''
    with pgdb.get_cursor() as cursor:
        cursor.execute(query)


@click.command("db-pre-compute")
@click.option(
    "--commit", 
    is_flag=True, 
    help="Commit the results directly to the database."
)
@click.option(
    "--no-header", 
    is_flag=True, 
    help="Do not print the schema before emiting INSERT queries."
)
def pre_compute(commit=False, no_header=False):
    '''Precompute all hazard data and store the results in the database.'''
    
    header = not no_header
    if header:
        with current_app.open_resource("schema.sql") as f:
            print(f.read().decode('utf-8'))

    # A list containing dictionaries and metadata for each hazard function.
    hazards = [
        dict(
            function_name='extreme_temp.intensity_from_return_time',
            function=extreme_temp.intensity_from_return_time,
            ci_report_url = 'data/extreme_temp/intensity_ci_report/{covariate}/{return_time}/{x}/{y}',
            arg_names=['covariate', 'return_time'],
            args=[
                [0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0], # Covariate/Global temperature anomaly
                list(range(10, 110, 10)),
            ]
        ),
        dict(
            function_name='extreme_temp.change_in_intensity',
            function=extreme_temp.change_in_intensity,
            ci_report_url = 'data/extreme_temp/intensity_change_ci_report/{covariate}/{return_time}/{covariate_comp}/{x}/{y}',
            arg_names=['return_time', 'covariate', 'covariate_comp'],
            args=[
                list(range(10, 110, 10)),
                [0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5], # Covariate/Global temperature anomaly
                [0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0], # Comparitave Covariate/Global temperature anomaly
            ]
        ),
        dict(
            function_name='extreme_temp.return_time_from_intensity',
            function=extreme_temp.return_time_from_intensity,
            ci_report_url = 'data/extreme_temp/return_time_ci_report/{covariate}/{intensity}/{x}/{y}',
            arg_names=['covariate', 'intensity'],
            args=[
                [0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0], # Covariate/Global temperature anomaly
                list(range(30, 41)),
            ]
        ),
        dict(
            function_name='extreme_temp.change_in_frequency',
            function=extreme_temp.change_in_frequency,
            ci_report_url = 'data/extreme_temp/frequency_change_ci_report/{covariate}/{intensity}/{covariate_comp}/{x}/{y}',
            arg_names=['intensity', 'covariate', 'covariate_comp'],
            args=[
                list(range(30, 41)),
                [0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5], # Covariate/Global temperature anomaly
                [0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0], # Comparitave Covariate/Global temperature anomaly
            ]
        ),
    ]

    insert_query_template = (
        "INSERT INTO hazard_data (function, central_estimate, geom, x_idx, y_idx, ci_report, {arg_names_clause}) VALUES {value_clauses};"
    )

    # Clear old data from the database.
    if commit:
        db_insert("DELETE FROM hazard_data;")

    for hazard in hazards:
        func = hazard['function']
        func_name = hazard['function_name']
        arg_names = hazard['arg_names']
        ci_report_url = hazard['ci_report_url']
        # Call each function with all combinations of input parameters.
        for arg in itertools.product(*hazard['args']):

            if 'covariate_comp' in arg_names and arg[1] >= arg[2]:
                continue

            composite_fit = extreme_temp.init_composite_fit(
                current_app.config['DATA_FILE_DESC'],
                simParams='c,loc1,scale1',
                nVariates=1000,
                preProcess=True,
            )

            # Unwrapping is needed to turn the 2D grid into a list of entries to be added to the database.
            # This is also a convinienc place to add the CI report url for each cell.
            central_estimate = func(composite_fit, *arg)
            params = dict(zip(arg_names, arg))
            unwrapped_central_estimate = [
                {**ce, 'ci_report_url': ci_report_url.format(x=ce['coord_idx'][1], y=ce['coord_idx'][0], **params)}
                for ce in unwrap_xarray(central_estimate)
            ]

            # Build the SQL query
            values_clauses = unwrapped_xarray_to_sql(func_name, unwrapped_central_estimate, arg)
            arg_names_clause = ', '.join(arg_names)
            query = insert_query_template.format(
                arg_names_clause=arg_names_clause, 
                value_clauses=', '.join(values_clauses)
            )

            if commit:
                db_insert(query)
            else:
                print(query)


def init_app(app):
    """Register database functions with the Flask application."""
    #app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_cli)
    app.cli.add_command(pre_compute)

