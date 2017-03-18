from .views import app
from .db_connection import graph

app.config.from_object('config')

graphNodes = [("User", "username"),
              ("Tag", "name"),
              ("Post", "id"),
              ("INode", "id"),
              ("ENode", "id"),
              ("SNode", "id"),
              ("SArc", "id"),
              ("Vote", "id")]


def create_uniqueness_constraint(label, property):
    query = "CREATE CONSTRAINT ON (n:{label}) ASSERT n.{property} IS UNIQUE"
    query = query.format(label=label, property=property)
    graph.cypher.execute(query)


for l, p in graphNodes:
    create_uniqueness_constraint(l, p)
