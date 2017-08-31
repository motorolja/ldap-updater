#!/usr/bin/env python3
# Handles queries to the LDAP backend
# Reads the LDAP server configuration from a JSON file

import sys
import logging
import getpass
import json
import ldap

class LDAPHelper():
    # Boolean to keep track of if a connection to LDAP-backend has been made
    first_connect = True

    # Backend server connection
    backend_server = None

    # LDAP backend to connect to
    ldap_server = ""
    ldap_version = -1

    # LDAP credentials
    ldap_user = ""
    ldap_password = ""

    # LDAP query parameters
    basedn = ""
    search_scope = ""
    search_filter = ""
    search_attribute = ""

    def __init__(self, config):
        self.load_configuration_from_file(config)

    # Load the configuration
    def load_configuration_from_file(self, config_file):
        logging.debug("Opening ldap config: " + config_file)
        with open(config_file, 'r') as f:
            config = json.load(f)
        logging.debug("Reading ldap config")
        self.ldap_server = config['ldap_server']
        self.ldap_version = config['ldap_version']
        self.ldap_user = config['ldap_user']
        self.basedn = config['basedn']
        self.search_scope = config['search_scope']
        self.search_filter = config['search_filter']
        self.search_attribute = config['search_attribute']
        try:
            self.ldap_password = getpass.getpass()
        except getpass.GetPassWarning:
            logging.info("Warning: System does not support echo free input, password input may be echoed")
        logging.info("Loaded LDAP config")

    # Connect to the LDAP backend
    def connect(config_file = "config.json"):
        logging.info("Trying to establish connection to LDAP server: {server}"
                     .format(server = self.ldap_server))
        # Connect to the backend
        self.backend_server = ldap.initialize('ldap://' + self.ldap_server)
        try:
            self.backend_server.protocol_version = self.ldap_version
            self.backend_server.simple_bind_s(self.ldap_user, self.ldap_password)
            valid = True
            logging.info("Established connection to LDAP server")
        except ldap.INVALID_CREDENTIALS:
            logging.error("Invalid login credentials")
            sys.exit(-1)
        except ldap.LDAPError as e:
            if type(e.message) == dict and e.message.has_key('desc'):
                logging.error(e.message['desc'])
            else:
                logging.error(e)
            sys.exit(-2)

    # Query the LDAP backend
    def ldap_query():
        logging.info("Starting to query LDAP server")
        # Query result asynchronus
        ldap_result_id = self.backend_server.search(self.basedn, self.search_scope, self.search_filter, self.search_attribute)
        result_set = []
        try:
            while 1:
                result_type, result_data = self.backend_server.result(ldap_result_id, 0)
                if (result_data == []):
                    break
                else:
                    if result_type == ldap.RES_SEARCH_ENTRY:
                        result_set.append(result_data)
            logging.info("Finished with query to LDAP server")
            return result_set
        except ldap.LDAPError as e:
            if type(e.message) == dict and e.message.has_key('desc'):
                logging.error(e.message['desc'])
            else:
                logging.error(e)
            sys.exit(-2)

    # Handle for executing predefined query
    def run_query():
        if self.first_connect:
            self.connect()
            self.first_connect = False
        result = self.ldap_query()
        return result
