#!/usr/bin/env python3

import sys
import socketserver
import logging
import json

from lib.MyTCPHandler import MyTCPHandler

# Load the server and TCP Handler configuration from file
def load_server_handler_config(config_file):
    logging.debug("Opening socketserver config: " + config_file)
    with open(config_file, 'r') as f:
        logging.debug("Reading socketserver config")
        config = json.load(f)
    HOST = config['host']
    PORT = config['port']
    logging.info("Loaded socketserver config")
    socketserver.TCPServer.allow_reuse_address = True
    logging.info("Attempting to listen on {host} tcp port {port}"
                 .format(host=HOST, port=PORT))
    return socketserver.TCPServer((HOST, PORT), MyTCPHandler(config_file))


# Start the socket server
def run_updater_server(config_file="config.json"):
    # Load socketserver config
    server = load_server_handler_config(config_file)
    logging.info("Now serving connections (abort with crtl-c).")
    # Run until the program is forcefully killed
    try:
        # Host a TCP-server on host at a specified port and handle connections
        server.serve_forever()
    except KeyboardInterrupt as ki:
        logging.info("Exiting due to keyboard interrupt.")
        sys.exit(0)
