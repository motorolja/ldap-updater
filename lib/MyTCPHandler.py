#!/usr/bin/env python3

import sys
import socketserver
import logging
import json
import subprocess

from lib.LDAPHelper import LDAPHelper

# Defines what happens after a connection has been made
class MyTCPHandler(socketserver.StreamRequestHandler):
    EXTERNAL_SCRIPT = ""
    LDAP_CONFIG = ""
    LAST_RUN = "lastrun"
    helper = None

    def __init__(self, config_file):
        self.load_configuration_from_file(config_file)
        self.helper = LDAPHelper(self.LDAP_CONFIG)

    def handle(self):
        # Read data from the client (only for debugging)
        # self.rfile is a file-like object created by the handler;
        self.data = self.rfile.readline().strip()
        logging.info("Connection accepted from: {}".format(self.client_address[0]))
        logging.debug("{} wrote:".format(self.client_address[0]))
        logging.debug(self.data)

        # Get the LDAP query result
        query_result = self.helper.run_query()
        # Compare with lastrun, if no diff do not execute external script
        diff = {}
        if self.changed_since_last_query(query_result, diff):
            # Pass the result to the external script
            logging.info("Starting executing external script:"
                         + self.EXTERNAL_SCRIPT)
            try:
                # For all lines in diff, run the external script
                for i in range(0, len(diff)):
                    logging.info("Passing following arguments to external script: "
                                 + diff[i])
                    subprocess.check_call(self.EXTERNAL_SCRIPT, diff[i])
            except subprocess.CalledProcessError as cpe:
                logging.error(cpe)
                logging.error("Error while trying to run external script: "
                              + self.EXTERNAL_SCRIPT)
        # Reply to the client to it closes the socket.
        # self.wfile is a file-like object used to write back
        status_message = "Request received and processed"
        self.wfile.write(status_message)

    def load_configuration_from_file(self, config_file):
        logging.debug("Opening handler config: " + config_file)
        with open(config_file, 'r') as f:
            logging.debug("Reading handler config")
            config = json.load(f)
        self.EXTERNAL_SCRIPT = config['external_script']
        if 'ldap_config' in config:
            self.LDAP_CONFIG = config['ldap_config']
        else:
            self.LDAP_CONFIG = config_file
        logging.info("Loaded socketserver config")

    # Check if the query is the same since last run
    def changed_since_last_query(new_query_result, diff):
        changed = False
        # If there is no data on last run create the file
        if not sys.os.path.exists(self.LAST_RUN):
            changed = True
            diff = new_query_result
        else:
            current_line = 0
            temp = 0
            with open(self.LAST_RUN, 'r') as f:
                for line in f:
                    for i in range(current_line, len(new_query_result)):
                        if line == new_query_result[i]:
                            temp = i
                            break
                        changed = True
                        diff += new_query_result[i]
                        current_line = temp
        if changed:
            # Write the query result to file
            with open(self.LAST_RUN, 'w+') as f:
                f.write(new_query_result)
        return changed
