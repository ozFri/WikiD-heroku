user = "neo4j"
password ="12345"
db_host_port = "localhost:7473"
db_url = "https://%s/db/data" % (db_host_port)
# This for username=neo4j, password='12345'
# Link to generate https://www.blitter.se/utils/basic-authentication-header-generator/
headers={'Authorization': 'Basic bmVvNGo6MTIzNDU='}

#link to neo4j graphql:
graphql_url='http://localhost:7474/graphql/'

is_secured = True
