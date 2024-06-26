"""
This file contains additional functions used in old_lux and luxdetails
"""
from sys import stderr, exit
from sqlite3 import connect
from contextlib import closing
import argparse
from table import Table

DATABASE_URL = "file:lux.sqlite?mode=ro"

def run_runserver_argparse():
    """
    this function displays different prompts based on the argument input for runserver.py
    """
    parser = argparse.ArgumentParser(prog='runserver.py', allow_abbrev=False,
                                         description='The YUAG search application')
    parser.add_argument('port', help='the port at which the server should listen')
    args = parser.parse_args()
    return args

def run_lux_argparse():
    """
    this function displays different prompts based on the argument input for lux.py
    """
    parser = argparse.ArgumentParser(prog='lux.py', allow_abbrev=False)
    parser.add_argument('-d', help='show only those objects whose date contains date', metavar='date')
    parser.add_argument('-a', help='show only those objects produced by an agent with name containing agt', metavar='agt')
    parser.add_argument('-c', help='show only those objects classified with a classifier having a name containing cls', metavar='cls')
    parser.add_argument('-l', help='show only those objects whose label contains label', metavar='label')
    args = parser.parse_args()
    return args

def run_luxdetails_argparse():
    """
    This function displays different prompts based on the argument input for lux_details.py
    """
    arg_parser = argparse.ArgumentParser(prog='luxdetails.py', allow_abbrev=False)
    arg_parser.add_argument('object', help='Object ID to retrieve details for', nargs=1)
    args, _ = arg_parser.parse_known_args()
    return args.object[0]

def connect_to_database(queries, filters):
    """
    query: statement to execute in SQL database
    filters: list of filter(s) to apply to SQL query (filling in "?" marks)
    fetch_method: "fetchall" or "fetchone"
    """
    # acquire a connection to db
    try:
        with connect(DATABASE_URL, uri=True) as connection:
            # create a cursor in the db
            with closing(connection.cursor()) as cursor:
                # use prepared statments to execute on db and retrieve results
                results = []
                for query in queries:
                    cursor.execute(query, filters)
                    results.append(cursor.fetchall())
                return results

    except Exception as err:
        print(f'Error: {err}', file=stderr)
        exit(1)

def output_objects(objects, col_names, format_str = None):
    """
    objects: the entire data we have and want to display (ideally, output of cursor.fetchall(). should be list of lists of strings)
    column_names: list of strings, will go in top of table as header
    """
    return Table(col_names, objects, format_str=format_str, max_width=float('inf'))