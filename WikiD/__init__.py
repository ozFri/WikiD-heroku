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
              ("VNode", "id")]


def create_uniqueness_constraint(label, prop):
    query = "CREATE CONSTRAINT ON (n:{label}) ASSERT n.{prop} IS UNIQUE"
    query = query.format(label=label, prop=prop)
    graph.run(query)


for l, p in graphNodes:
    create_uniqueness_constraint(l, p)
