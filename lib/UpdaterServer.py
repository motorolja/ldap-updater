#!/usr/bin/env python3

import sys
import socketserver
import logging
import json

from lib.LDAPHelper import connect, find_users

# TODO: parse the command line for arguments:
# - Host
# - Port
# - Help
# - Version
HOST = ""
PORT = 0

# Defines what happens after a connection has been made
class MyTCPHandler(socketserver.StreamRequestHandler):

    def handle(self):
        # Read data from the client (only for debugging)

        # self.rfile is a file-like object created by the handler;
        self.data = self.rfile.readline().strip()
        logging.info("{} wrote:".format(self.client_address[0]))
        logging.info(self.data)

        ldap_backend = connect()
        find_users(ldap_backend)
        # Reply to the client to it closes the socket.
        # self.wfile is a file-like object used to write back
        status_message = "Request received and processed"
        self.wfile.write(status_message)

# Load the socketserver configuration from file
def load_socketserver_config(config_file):
    with open(config_file, 'r') as f:
        config = json.load(f)
    HOST = config['host']
    PORT = config['port']

# Start the socket server
def run_updater_server(config_file = "config.json"):
    # Load socketserver config
    load_socketserver_config(config_file)
    # Host a TCP-server on host at a specified port and handle connections
    # in accordance to the specified handler
    server = socketserver.TCPServer((HOST, PORT), MyTCPHandler)
    # Run until the program is forcefully killed
    try:
        server.serve_forever()
    except KeyboardInterrupt as ki:
        logging.info("Exiting due to keyboard interrupt.")
        sys.exit(0)
