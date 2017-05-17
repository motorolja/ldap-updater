# Handles queries to the LDAP backend
# Reads the LDAP server configuration from a JSON file

import json
import ldap

# TODO:
# 1. Queries to get current list of users in LDAP database
# 2. Compare with local list of users to see if there are any not processed
# 3. Run external script (add script variables in config.json) if there are new users
# 4. Update local list with the new users
# 5. Return meaningful status message

# Boolean to keep track of if the configuration file has been loaded
first_connect = True
# The default config filename
config_file = 'config.json'

# Load the configuration from file
def load_config():
    with open(config_file, 'r') as f:
        config = json.load(f)
    ldap_server = config['ldap_server']
    ldap_version = config['ldap_version']
    ldap_password = config['ldap_password']
    ldap_user = config['ldap_user']

# Connect to the LDAP backend
def connect():
    # Load the config if it has not been loaded
    if first_connect:
        load_config()
        first_connect = False
    # Connect to the backend
    backend_server = ldap.initialize('ldap://' + ldap_server)
    try:
        backend_server.protocol_version = ldap_version
        backend_server.simple_bind_s(ldap_user, ldap_password)
        valid = True
        return backend_server
    except ldap.INVALID_CREDENTIALS:
        print("Invalid login credentials")
        sys.exit(-1)
    except ldap.LDAPError as e:
        if type(e.message) == dict and e.message.has_key('desc'):
            print(e.message['desc'])
        else:
            print(e)
        sys.exit(-2)

# Query the LDAP backend
def find_users(backend_server, base_dn, search_scope, search_filter, search_attribute):
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
        return result_set
    except ldap.LDAPError as e:
        if type(e.message) == dict and e.message.has_key('desc'):
            print(e.message['desc'])
        else:
            print(e)
        sys.exit(-2)
