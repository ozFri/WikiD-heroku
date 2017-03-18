from py2neo import Graph, Node, Relationship, authenticate
from passlib.hash import bcrypt
from .db_connection import graph
from flask import session
from datetime import datetime
import os
import uuid

def create_new_event(user, event_name="General"):
    event = Node(
        "ENode",
        id=str(uuid.uuid4()),
        name=event_name,
        timestamp=timestamp(),
        date=date()
    )
    graph.create(event)
    graph.create_unique(Relationship(user, "OBSERVES", event))
    return event

def create_new_schema_relationship(source, schemaID, target):
    sourceNode=get_iNode_by_title(source)
    targetNode=get_iNode_by_title(target)
    schemaNode=get_sNode(schemaID)
    graph.create(Relationship(sourceNode,"SArc",schemaNode))
    graph.create(Relationship(schemaNode,"SArc",targetNode))

def get_iNode(inode_id):
    return graph.find_one("INode", "id", inode_id)

def get_iNode_by_title(inode_title):
    return graph.find_one("INode", "title", inode_title)
def get_sNode(snode_id):
    return graph.find_one("SNode", "id", snode_id)

def get_todays_recent_posts():
    query = """
    MATCH (user:User)-[:PUBLISHED]->(inode:INode)
    WHERE inode.date = {today}
    RETURN user.username AS username, inode
    ORDER BY inode.timestamp DESC LIMIT 5
    """
    return graph.cypher.execute(query, today=date())

def timestamp():
    epoch = datetime.utcfromtimestamp(0)
    now = datetime.now()
    delta = now - epoch
    return delta.total_seconds()

def date():
    return datetime.now().strftime('%F')

class INode:

    def __init__(self, iNodeId):
        self.id = iNodeId
        self.node = get_iNode(iNodeId)
        self.inodes = self.get_iNodes()
        self.title = self.node.properties["title"]
        self.supporting = self.get_supporting()
        self.opposing = self.get_opposing()
        self.supported = self.get_supported()
        self.opposed = self.get_opposed()
        self.agreeing = self.get_votes("AGREES_WITH")
        self.disagreeing = self.get_votes("DISAGREES_WITH")
        self.undecided = self.get_votes("UNDECIDED_ON")
        self.user_vote = self.user_vote()

    def get_iNodes(self):
        query = """
        MATCH (user:User)-[:PUBLISHED]->(inode:INode)
        RETURN user.username AS username, inode
        ORDER BY inode.timestamp DESC LIMIT 5000
        """

        return graph.cypher.execute(query)

    def get_supporting(self):
        query = """
        MATCH (inode)-[:SArc]->(snode:SNode{schema:"supports"})-[:SArc]->({title:""" + '"' + self.title + '"' + """ })
        RETURN DISTINCT inode
        ORDER BY inode.timestamp DESC LIMIT 5
        """
        return graph.cypher.execute(query)

    def get_opposing(self):
        query = """
        MATCH (inode)-[:SArc]->(snode:SNode{schema:"opposes"})-[:SArc]->({title:""" + '"' + self.title + '"' + """ })
        RETURN DISTINCT inode,snode
        ORDER BY inode.timestamp DESC LIMIT 5
        """
        return graph.cypher.execute(query)

    def get_supported(self):
        query = """
        MATCH (inode)<-[:SArc]-(snode:SNode{schema:"supports"})<-[:SArc]-({title:""" + '"' + self.title + '"' + """ })
        RETURN DISTINCT inode
        ORDER BY inode.timestamp DESC LIMIT 5
        """
        return graph.cypher.execute(query)

    def get_opposed(self):
        query = """
        MATCH (inode)<-[:SArc]-(snode:SNode{schema:"opposes"})<-[:SArc]-({title:""" + '"' + self.title + '"' + """ })
        RETURN DISTINCT inode,snode
        ORDER BY inode.timestamp DESC LIMIT 5
        """
        return graph.cypher.execute(query)


    def user_vote(self):
        query = """
        MATCH (User{username:"""+'"'+session["username"]+'"'+"""})-[OBSERVES]->(ENode{name:"""+'"'+session["eventname"]+'"'+"""})-[vote]->(INode{title:"""+'"'+self.title+'"'+"""})
        RETURN vote
        """
        return graph.cypher.execute(query)

    def get_votes(self,vote_type):
        query = """
        MATCH (User)-[OBSERVES]->(ENode{name:"""+'"'+session["eventname"]+'"'+"""})-[vote:"""+vote_type+"""]->(INode{title:"""+'"'+self.title+'"'+"""})
        RETURN count(DISTINCT vote) as votes
        """
        return graph.cypher.execute(query).one
