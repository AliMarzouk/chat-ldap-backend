import os

from myChannelTuto.settings import BASE_DIR

ldap_login = "cn=admin,dc=example,dc=org"
ldap_base = "dc=example,dc=org"
ldap_password = 'admin'


ca_path = os.path.join(BASE_DIR, 'chat/shared/ca/ca.crt')
ca_key_path = os.path.join(BASE_DIR, 'chat/shared/ca/ca.key')

private_key_path = os.path.join(BASE_DIR, 'chat/shared/server_certif/server.key')
public_key_path = os.path.join(BASE_DIR, 'chat/shared/server_certif/server.pb')

crt_path = os.path.join(BASE_DIR, 'chat/shared/server_certif/server.crt')
