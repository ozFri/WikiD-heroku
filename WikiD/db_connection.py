from py2neo import Graph, authenticate
from urllib.parse import urlparse, urlunparse 
import os

url = urlparse(os.environ.get('GRAPHENEDB_URL', 'http://localhost:7474'))

url_without_auth = urlunparse((url.scheme, "{0}:{1}".format(url.hostname, url.port), '', None, None, None))
user = url.username
password = url.password

print(url_without_auth)
authenticate(url_without_auth, user, password)
graph = Graph(url_without_auth, bolt = False)

print(url + '\n' + username)


def DbConnection():
    authenticate(url_without_auth, user, password)
    graph = Graph(url_without_auth, bolt = False)
    return graph()

graph= setGraph()
