#!/usr/bin/env python3
# Handles queries to the LDAP backend
# Reads the LDAP server configuration from a JSON file

import sys
import logging
import getpass
import json
import ldap

# TODO:
# 1. Compare with previous result to see if there are any not processed
# 2. Run external script if there are diffs
# 3. Update local list with the new users
# 4. Return meaningful status message

# Boolean to keep track of if the configuration file has been loaded
first_connect = True

# Load the configuration
def load_config(config_file):
    logging.debug("Opening ldap config: " + config_file)
    with open(config_file, 'r') as f:
        config = json.load(f)
    logging.debug("Reading ldap config")
    ldap_server = config['ldap_server']
    ldap_version = config['ldap_version']
    ldap_user = config['ldap_user']
    search_scope = config['search_scope']
    search_filter = config['search_filter']
    search_attribute = config['search_attribute']
    try:
        ldap_password = getpass.getpass()
    except getpass.GetPassWarning:
        logging.info("Warning: System does not support echo free input, password input may be echoed")
    logging.info("Loaded LDAP config")

# Connect to the LDAP backend
def connect(config_file = "config.json"):
    # Load the config if it has not been loaded
    if first_connect:
        load_config(config_file)
        first_connect = False
    logging.info("Trying to establish connection to LDAP server: {server}"
                 .format(server = ldap_server))
    # Connect to the backend
    backend_server = ldap.initialize('ldap://' + ldap_server)
    try:
        backend_server.protocol_version = ldap_version
        backend_server.simple_bind_s(ldap_user, ldap_password)
        valid = True
        logging.info("Established connection to LDAP server")
        return backend_server
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
def find_users(backend_server):
    logging.info("Starting to query LDAP server")
    # Query result asynchronus
    ldap_result_id = backend_server.search(basedn, search_scope, search_filter, search_attribute)
    result_set = []
    try:
        while 1:
            result_type, result_data = backend_server.result(ldap_result_id, 0)
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
