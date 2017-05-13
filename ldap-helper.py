# Handles queries to the LDAP backend
# Reads the LDAP server configuration from a JSON file

import json
import ldap

first_connect = True
# The default config filename
config_file = 'config.json'

def load_config():
    with open(config_file, 'r') as f:
        config = json.load(f)
    ldap_server = config['ldap_server']
    ldap_version = config['ldap_version']
    ldap_password = config['ldap_password']
    ldap_user = config['ldap_user']

def connect():
    if first_connect:
        load_config()
        first_connect = False
    l = ldap.initialize('ldap://' + ldap_server)
    try:
        l.protocol_version = ldap.VERSION3 # parse this from config instead
        l.simple_bind_s(ldap_user, ldap_password)
        valid = True
    except ldap.INVALID_CREDENTIALS:
        print "Invalid login credentials"
        sys.exit(-1)
    except ldap.LDAPError, e:
        if type(e.message) == dict and e.message.has_key('desc'):
            print e.message['desc']
        else:
            print e
        sys.exit(-2)
