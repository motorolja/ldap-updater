#!/usr/bin/env python3

import sys
import socketserver
import logging
import json

from lib.LDAPHelper import connect, find_users

HOST = ""
PORT = 0

# Defines what happens after a connection has been made
class MyTCPHandler(socketserver.StreamRequestHandler):

    def handle(self):
        # Read data from the client (only for debugging)

        # self.rfile is a file-like object created by the handler;
        self.data = self.rfile.readline().strip()
        logging.info("Connection accepted from: {}".format(self.client_address[0]))
        logging.debug("{} wrote:".format(self.client_address[0]))
        logging.debug(self.data)

        ldap_backend = connect()
        find_users(ldap_backend)
        # Reply to the client to it closes the socket.
        # self.wfile is a file-like object used to write back
        status_message = "Request received and processed"
        self.wfile.write(status_message)

# Load the socketserver configuration from file
def load_socketserver_config(config_file):
    logging.debug("Opening socketserver config: " + config_file)
    with open(config_file, 'r') as f:
        config = json.load(f)
    logging.debug("Reading socketserver config")
    HOST = config['host']
    PORT = config['port']
    logging.info("Loaded socketserver config")

# Start the socket server
def run_updater_server(config_file = "config.json"):
    # Load socketserver config
    load_socketserver_config(config_file)
    # Host a TCP-server on host at a specified port and handle connections
    # in accordance to the specified handler
    logging.info("Attempting to listen on {host} tcp port {port}"
                 .format(host = HOST, port = PORT))
    socketserver.TCPServer.allow_reuse_address = True
    server = socketserver.TCPServer((HOST, PORT), MyTCPHandler)

    logging.info("Now serving connections (abort with crtl-c).")
    # Run until the program is forcefully killed
    try:
        server.serve_forever()
    except KeyboardInterrupt as ki:
        logging.info("Exiting due to keyboard interrupt.")
        sys.exit(0)
