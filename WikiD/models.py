from py2neo import Graph, Node, Relationship, authenticate
from passlib.hash import bcrypt
from .db_connection import graph
from datetime import datetime
import os
import uuid


class Post:

    def __init__(self, postid):
        self.node = get_post(postid)
        self.posts = self.get_posts()
        self.title = self.node.properties["title"]
        self.supporting = self.get_supporting()
        self.opposing = self.get_opposing()
        self.supported = self.get_supported()
        self.opposed = self.get_opposed()

    def get_posts(self):
        query = """
        MATCH (user:User)-[:PUBLISHED]->(post:Post)
        RETURN user.username AS username, post
        ORDER BY post.timestamp DESC LIMIT 5
        """

        return graph.cypher.execute(query)

    def get_supporting(self):
        query = """
        MATCH (post)-[]->(snode:Snode{schema:"Supports"})-[]->({title:""" + '"' + self.title + '"' + """ })
        RETURN post,snode
        ORDER BY post.timestamp DESC LIMIT 5
        """
        return graph.cypher.execute(query)

    def get_opposing(self):
        query = """
        MATCH (post)-[]->(snode:Snode{schema:"Opposes"})-[]->({title:""" + '"' + self.title + '"' + """ })
        RETURN post,snode
        ORDER BY post.timestamp DESC LIMIT 5
        """
        return graph.cypher.execute(query)

    def get_supported(self):
        query = """
        MATCH (post)<-[]-(snode:Snode{schema:"Supports"})<-[]-({title:""" + '"' + self.title + '"' + """ })
        RETURN post,snode
        ORDER BY post.timestamp DESC LIMIT 5
        """
        return graph.cypher.execute(query)

    def get_opposed(self):
        query = """
        MATCH (post)<-[]-(snode:Snode{schema:"Opposes"})<-[]-({title:""" + '"' + self.title + '"' + """ })
        RETURN post,snode
        ORDER BY post.timestamp DESC LIMIT 5
        """
        return graph.cypher.execute(query)


def create_new_event(user, event_name="General"):
    event = Node(
        "Enode",
        id=str(uuid.uuid4()),
        name=event_name,
        timestamp=timestamp(),
        date=date()
    )
    graph.create(event)
    graph.create_unique(Relationship(user, "OBSERVES", event))
    return event


def get_post(post_id):
    return graph.find_one("Post", "id", post_id)


def get_todays_recent_posts():
    query = """
    MATCH (user:User)-[:PUBLISHED]->(post:Post)
    WHERE post.date = {today}
    RETURN user.username AS username, post
    ORDER BY post.timestamp DESC LIMIT 5
    """
    return graph.cypher.execute(query, today=date())


def timestamp():
    epoch = datetime.utcfromtimestamp(0)
    now = datetime.now()
    delta = now - epoch
    return delta.total_seconds()


def date():
    return datetime.now().strftime('%F')
