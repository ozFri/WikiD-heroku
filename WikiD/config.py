import types
#LOCAL SETTINGS
user = "neo4j"
password ="neo4j1"
db_host_port = "localhost:7473"
db_url = "https://%s/db/data" % (db_host_port)
headers={'Authorization': 'Basic bmVvNGo6MTIzNDU='}

#REMOTE SETTINGS
heroku=types.SimpleNamespace()
heroku.user = "app45980694-jSDTJQ"
heroku.password ="b.Dn3Ho4YY9uNa.OI0SJoL7PTg0HLoq"
heroku.db_host_port = "hobby-lcnmpbakabdmgbkenghdlhbl.dbs.graphenedb.com:24780"
heroku.db_url =  "https://%s/db/data" % (db_host_port)
# This for username=neo4j, password='12345'
# Link to generate https://www.blitter.se/utils/basic-authentication-header-generator/
heroku.headers={'Authorization': 'b.Dn3Ho4YY9uNa.OI0SJoL7PTg0HLoq'}
#link to neo4j graphql:
graphql_url= db_url + '/graphql/'

is_secured = True
