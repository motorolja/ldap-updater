#!/usr/bin/env python3

import sys
import socketserver
import logging
import json
import subprocess

from lib.LDAPHelper import run_query

HOST = ""
PORT = 0
LDAP_CONFIG = ""
EXTERNAL_SCRIPT = ""
LAST_RUN = "lastrun"

# Defines what happens after a connection has been made
class MyTCPHandler(socketserver.StreamRequestHandler):

    def handle(self):
        # Read data from the client (only for debugging)
        # self.rfile is a file-like object created by the handler;
        self.data = self.rfile.readline().strip()
        logging.info("Connection accepted from: {}".format(self.client_address[0]))
        logging.debug("{} wrote:".format(self.client_address[0]))
        logging.debug(self.data)

        # Get the LDAP query result
        query_result = run_query(LDAP_CONFIG)
        # Compare with lastrun, if no diff do not execute external script
        if changed_since_last_query(query_result):
            # Pass the result to the external script
            logging.info("Passing query result to external script")
            try:
                subprocess.check_call(EXTERNAL_SCRIPT, LAST_RUN)
            except subprocess.CalledProcessError as cpe:
                logging.error(cpe)
                logging.error("Error while trying to run external script: "
                              + EXTERNAL_SCRIPT)
                # Reply to the client to it closes the socket.
                # self.wfile is a file-like object used to write back
        status_message = "Request received and processed"
        self.wfile.write(status_message)

# Check if the query is the same since last run
def changed_since_last_query(new_query_result):
    changed = False
    # If there is no data on last run create the file
    if not os.path.exists(LAST_RUN):
       changed = True
    else:
        with open(LAST_RUN, 'r') as f:
            for lineA in f and lineB in new_query_result:
                if lineA != lineB:
                    changed = True
                    break
    if changed:
        # Write the query result to file
        with open(LAST_RUN, 'w+') as f:
            f.write(new_query_result)
    return changed


# Load the server and TCP Handler configuration from file
def load_server_handler_config(config_file):
    logging.debug("Opening socketserver config: " + config_file)
    with open(config_file, 'r') as f:
        config = json.load(f)
    logging.debug("Reading socketserver config")
    HOST = config['host']
    PORT = config['port']
    EXTERNAL_SCRIPT = config['external_script']
    if 'ldap_config' in config:
        LDAP_CONFIG = config['ldap_config']
    else:
        LDAP_CONFIG = config_file
    logging.info("Loaded socketserver config")

# Start the socket server
def run_updater_server(config_file = "config.json"):
    # Load socketserver config
    load_server_handler_config(config_file)
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
