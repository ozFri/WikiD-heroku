from py2neo import Graph, authenticate
import os

url = str(os.environ.get('GRAPHENEDB_URL', 'http://localhost:7474'))
username = str(os.environ.get('NEO4J_USERNAME'))
password = str(os.environ.get('NEO4J_PASSWORD'))

print(url + '\n' + username)


def DbConnection():
    authenticate(url.strip('http://'), username, password)
    return Graph(url + '/db/data/')


def setGraph():
    graph = DbConnection()
    global graph
