import traceback

from chat.shared.client import Client
from chat.shared.global_settings import ldap_login, ldap_base, ldap_password
from ldap3 import *


class LDAP_server:
    def __init__(self, uri='ldap://ldapdnjksnfljhqksjhflk', login=ldap_login, password=ldap_password):
        self.server = Server(uri)
        self.ldap_base = ldap_base
        print(login)
        self.connection = Connection(self.server, user=login, password=password, auto_bind=True, auto_referrals=False)

    def create(self, client: Client):
        # create a client in LDAP server
        # Return TRUE if a new entry for client is created
        # Return FALSE if the entry already exists or is not created
        classObjects = ['inetOrgPerson', 'person']
        return self.connection.add('cn={},{}'.format(client.login, self.ldap_base), classObjects,
                                   {'uid': client.nom, 'sn': client.prenom, 'userPassword': client.password,
                                    'cn': client.login, 'telephoneNumber': client.num,
                                    'description': client.certification})

    def find_client(self, login):
        try:
            self.connection.search(self.ldap_base, '(cn=' + login + ')',
                                   attributes=['uid', 'cn', 'sn', 'userPassword', 'telephoneNumber', 'description'])
            # bool = self.connection.add('cn=mohsen,dc=example,dc=org', ['inetOrgPerson', 'person'],
            #                            {'cn': 'mohsen', 'sn': 'client.prenom', 'userPassword': 'client.password',
            #                             'telephoneNumber': 'client.num', 'description': 'client.certification'})
            values = self.connection.entries[0]
            # print(values)
            cl = Client(values['telephoneNumber'].value, values['uid'].value, values['sn'].value, values['cn'].value,
                        values['userPassword'].value, values['description'].value)

            return cl
        except:
            traceback.print_exc()
            return None


class Server:
    ldap_server = LDAP_server()
