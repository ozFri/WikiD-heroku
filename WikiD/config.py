#LOCAL SETTINGS
#user = "neo4j"
#password ="neo4j1"
#db_host_port = "7473"
#db_url =  "localhost:" % (db_host_port)
#headers={'Authorization': 'Basic bmVvNGo6MTIzNDU='}

#REMOTE SETTINGS
user = "app45980694-1SqesOw"
password ="b.XYhdVctgD8b0.jsxxlTdB848loItn"
db_host_port = "24786"
db_url =  "bolt://hobby-hankpoiekhacgbkegaaijpal.dbs.graphenedb.com:" % (db_host_port)
# This for username=neo4j, password='12345'
# Link to generate https://www.blitter.se/utils/basic-authentication-header-generator/
headers={'Authorization': 'Basic YXBwNDU5ODA2OTQtMVNxZXNPdzo9ImIuWFloZFZjdGdEOGIwLmpzeHhsVGRCODQ4bG9JdG4='}

#link to neo4j graphql:
graphql_url= db_url + '/graphql/'

is_secured = True
