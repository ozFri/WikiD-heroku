from .views import app
from .models import graph

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

create_uniqueness_constraint("User", "username"),
create_uniqueness_constraint("Tag", "name"),
create_uniqueness_constraint("Post", "id"),
create_uniqueness_constraint("INode", "id"),
create_uniqueness_constraint("ENode", "id"),
create_uniqueness_constraint("SNode", "id"),
create_uniqueness_constraint("SArc", "id"),
create_uniqueness_constraint("VNode", "id")
