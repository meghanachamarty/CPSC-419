"""
This file perform queries to the SQLite database

Author: Meghana and Ananya
"""

import pickle
from socket import socket, SOL_SOCKET, SO_REUSEADDR
from os import name
from sys import argv, stderr
from sys import exit
from luxdetails import main as luxdetails
from old_lux import main as old_lux

def handle_client(sock):
    """
    The handle_client function runs the luxdetails or old_lux to
    retrieve information from SQL database
    """
    try:
        # read in from client
        in_flo = sock.makefile(mode='rb')

        try:
            data = pickle.load(in_flo)

        except Exception as err:
            print(f"Error in pickle.load: {err}", file=stderr)

        # check length of input
        if len(data) == 1:
            # if 1, then run luxdetails.py
            print("reached if clause")
            server_table = luxdetails(data)
            print('lux details table:', server_table)
            print('Running luxdetails.py' if len(data) == 1 else 'Running old_lux.py')
        elif len(data) == 4:
            # if 4, then run old_lux.py
            reordered_data = [data[1]] + [data[3]] + [data[2]] + [data[0]]
            print("running old lux")
            server_table = old_lux(reordered_data)

        # pickle table, then print to flo and flush to client
        out_flo = sock.makefile(mode='wb')
        pickle.dump(server_table, out_flo)
        out_flo.flush()
        print('Sending data back to client')

    except Exception as err:
        print(f"Error in handle_client: {err}", file=stderr)

def help_arg():
    """
    This function handles the [-h] argument case
    """
    print("usage: luxserver.py [-h] port")
    print()
    print("Server for the YUAG application")
    print()
    print("positional arguments:")
    print("  port        the port at which the server should listen")
    print()
    print("optional arguments:")
    print("  -h, --help  show this help message and exit")
    exit(1)

def main():
    """
    This is the main function that handle errors and communicates with the client via socket
    """
    if len(argv) == 2 and (argv[1] == '-h' or argv[1] == '--help'):
        help_arg()

    if len(argv) != 2:
        print('Usage: python %s port' % argv[0])
        exit(1)

    try:
        # Set up Socket (Server)
        try:
            port = int(argv[1])

        except ValueError:
            print("The second argument is not a valid integer.")
            exit(1)

        server_sock = socket()
        # print('Opened server socket')

        if name != 'nt':
            server_sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)

        # Bind server socket to port
        try:
            server_sock.bind(('', port))
        except Exception:
            print(f"Port {port} is unavailable")
            exit(1)

        # Server is listening
        server_sock.listen()

        while True:
            try:
                sock, client_addr = server_sock.accept()
                with sock:
                    print('Client IP addr and port:', client_addr)
                    handle_client(sock)

            except Exception as ex:
                print(ex, file=stderr)

    except Exception as ex:
        print(ex, file=stderr)
        exit(1)

if __name__ == '__main__':
    main()
