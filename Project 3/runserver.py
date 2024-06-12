
#-----------------------------------------------------------------------
# runserver.py
# Author: Ananya and Meghana
#-----------------------------------------------------------------------

from utils_lux import run_runserver_argparse
from sys import stderr, argv, exit
from os import system
from luxapp import app

DATABASE_URL = "file:lux.sqlite?mode=ro"

def main():
    filters = run_runserver_argparse()
    # Your application code should not be in your runserver.py program, 
    # which should do nothing but start a Flask server on the provided port number
    if len(argv) != 2:
        print('Usage: ' + argv[0] + ' port', file=stderr)
        exit(1)

    try:
        port = int(argv[1])
    except Exception:
        print('Port must be an integer.', file=stderr)
        exit(1)
    
    try:
        app.run(host='0.0.0.0', port=port, debug=True)
    except Exception as ex:
        print(ex, file=stderr)
        exit(1)

if __name__ == '__main__':
    main()