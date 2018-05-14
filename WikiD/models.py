from py2neo import Graph, Node, Relationship, authenticate
from passlib.hash import bcrypt
from flask import session
from datetime import datetime
import os
import uuid

from . import config

authenticate(config.db_host_port, config.user, config.password)
graph = Graph(config.db_url, bolt = False, secure=config.is_secured)

def create_new_vote(user, vote_type, event, node):
    vote = Node(
        "VNode",
        id=str(uuid.uuid4()),
        name=vote_type,
        timestamp=timestamp(),
        date=date()
    )
    graph.create(vote)
    graph.merge(Relationship(user, "VOTED", vote))
    graph.merge(Relationship(vote, "APPLIES_TO", event))
    graph.merge(Relationship(vote, "APPLIES_TO", node))
    graph.merge(Relationship(user, "FOLLOWS", node))
    return event

def create_new_event(user, event_name="General"):
    event = Node(
        "ENode",
        id=str(uuid.uuid4()),
        name=event_name,
        timestamp=timestamp(),
        date=date()
    )
    graph.create(event)
    graph.merge(Relationship(user, "OBSERVES", event))
    return event

def add_item_to_feed(feedItem,node):
    query = """
    MATCH (node)
    WHERE node.id={nodeid}
    OPTIONAL MATCH (node)-[r:ACTIVITY_FEED]-(secondlatestitem)
    DELETE r
    RETURN secondlatestitem
    """
    oldfeed = graph.run(query,nodeid=node['id']).evaluate()
    graph.create(Relationship(node,"ACTIVITY_FEED",feedItem))
    if oldfeed is not None:
        graph.create(Relationship(feedItem,"ACTIVITY_FEED_NEXT",oldfeed))

def create_feed_item(actor,target,label):
    feedItem= Node(
            "FeedItem",
            id=str(uuid.uuid4()),
            actor=actor['username'],
            actor_id=actor['<id>'],
            target=target['title'],
            target_id=target['id'],
            label=label,
            timestamp=timestamp(),
            date=date()
            )
    graph.create(Relationship(feedItem, "TARGET", target))
    graph.create(Relationship(feedItem, "ACTOR", actor))
    return feedItem

# def add_tag_to_aifnode(aifNode, tag):

def create_new_schema_relationship(source, schemaID, target):
    sourceNode=get_aifNode_by_title(source)
    targetNode=get_aifNode_by_title(target)
    schemaNode=get_sNode(schemaID)
    graph.create(Relationship(sourceNode,"SArc",schemaNode))
    graph.create(Relationship(schemaNode,"SArc",targetNode))

def get_aifNode(inode_id):
    ret = graph.find_one("INode", "id", inode_id)
    if not ret:
        ret = graph.find_one("SNode", "id", inode_id)
    return ret

def get_aifNode_by_title(aifnode_title):
    ret = graph.find_one("INode", "title", aifnode_title)
    if not ret:
        ret = graph.find_one("SNode", "title", aifnode_title)
    return ret
def get_sNode(snode_id):
    return graph.find_one("SNode", "id", snode_id)

def get_aifNodes():
    query= """
    MATCH (user:User)-[:PUBLISHED]->(aifnode)
    RETURN user.username AS username, aifnode
    ORDER BY aifnode.timestamp DESC LIMIT 5000
    """
    return graph.run(query).data()

def timestamp():
    epoch = datetime.utcfromtimestamp(0)
    now = datetime.now()
    delta = now - epoch
    return delta.total_seconds()

def date():
    return datetime.now().strftime('%F')


def rename_iNode(inode_id,new_title):
    iNode=get_aifNode(inode_id)
    iNode["title"]=new_title
        
class AIFNode:
    def __init__(self, aifNodeID):
        self.id = aifNodeID
        self.aifnode = get_aifNode(aifNodeID)
        self.aifnodes = get_aifNodes()
        self.type = self.aifnode.labels
        if "SNode" in self.type():
            self.schema = self.aifnode.properties["schema"]
            self.source = self.aifnode.properties["source"]
            self.target = self.aifnode.properties["target"]
            self.source_id = self.aifnode.properties["source_id"]
            self.target_id = self.aifnode.properties["target_id"]
        self.title = self.aifnode.properties["title"]
        self.supporting = self.get_neighbours("supporting")
        self.opposing = self.get_neighbours("opposing")
        self.supported = self.get_neighbours("supported")
        self.opposed = self.get_neighbours("opposed")
        self.agreeing = self.get_votes("Agree")
        self.disagreeing = self.get_votes("Disagree")
        self.undecided = self.get_votes("Undecided")
        self.user_vote = self.user_vote()
        self.activity_feed = self.get_activity_feed()

    def get_neighbours(self,inference):
        reltype={"supporting": ("supports","-[:SArc]->"),
                 "supported" : ("supports","<-[:SArc]-"),
                 "opposing"  : ("opposes","-[:SArc]->"),
                 "opposed"   : ("opposes","<-[:SArc]-")
                 }
        query = """
        MATCH (aifnode)"""+reltype[inference][1]+"""(snode:SNode{schema:"""+'"'+reltype[inference][0]+'"'+"""})"""+reltype[inference][1]+"""({id:""" + '"' + self.id + '"' + """ })
        RETURN DISTINCT snode
        ORDER BY snode.timestamp DESC LIMIT 5000
        """
        return graph.run(query)

    def user_vote(self):
        username = session.get("username")
        if username is None:
            return
        query = """
        MATCH (User{username:"""+'"'+session["username"]+'"'+"""})-[OBSERVES]->(ENode{name:"""+'"'+session["eventname"]+'"'+"""})-[vote]->(SNode{title:"""+'"'+self.title+'"'+"""})
        RETURN vote
        """
        return graph.run(query)

    def get_votes(self,vote_type):
        eventname = session.get("eventname")
        if eventname is None:
            eventname = "General"
        query = """
        MATCH (vote) WHERE (:User)-[:VOTED]->(vote:VNode)-[:APPLIES_TO]->(:ENode{name:"""+'"'+eventname+'"'+"""}) AND (vote{name:"""+'"'+vote_type+'"'+"""})-[:APPLIES_TO]->({title:"""+'"'+self.title+'"'+"""})
        RETURN count(DISTINCT vote) as votes
        """
        return graph.run(query).evaluate()

    def get_activity_feed(self):
        query = """
        MATCH (n) WHERE n.id = {node_id}
        MATCH (n),(latest) WHERE (n)-[:ACTIVITY_FEED]->(latest:FeedItem)
        MATCH (latest)-[:ACTIVITY_FEED_NEXT*""" + '0' + """..""" + '100' + """]->(item:FeedItem)
        MATCH (item)-[:TARGET]->(target)
        MATCH (item)-[:ACTOR]->(actor)
        RETURN DISTINCT item, actor, target
        """
        return graph.run(query,node_id=self.id).evaluate()

    def delete(self):
        graph.run("""MATCH (n) where n.id="""+'"'+self.id+'"'+""" DETACH DELETE n""")
