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
    l = ldap.initialize('ldap://' + ldap_server)
    try:
        l.protocol_version = ldap_version
        l.simple_bind_s(ldap_user, ldap_password)
        valid = True
    except ldap.INVALID_CREDENTIALS:
        print("Invalid login credentials")
        sys.exit(-1)
    except ldap.LDAPError as e:
        if type(e.message) == dict and e.message.has_key('desc'):
            print(e.message['desc'])
        else:
            print(e)
        sys.exit(-2)
