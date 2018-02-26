from py2neo import Graph, Node, Relationship, authenticate
from passlib.hash import bcrypt
from .models import timestamp, date, create_new_event,create_new_vote, get_aifNode_by_title, get_aifNode
from .models import graph
from datetime import datetime
import uuid
import os

class User:

    def __init__(self, username):
        self.username = username

    def find(self):
        user = graph.find_one("User", "username", self.username)
        return user

    def register(self, password):
        if not self.find():
            user = Node("User", username=self.username,
                        password=bcrypt.encrypt(password))
            graph.create(user)
            return True
        else:
            return False

    def verify_password(self, password):
        user = self.find()
        if user:
            return bcrypt.verify(password, user['password'])
        else:
            return False

    def add_S_Node(self,schema,source,target):
        user= self.find()
        schemaNode= Node(
                "SNode",
                id=str(uuid.uuid4()),
                schema=schema,
                source=source,
                source_id=get_aifNode_by_title(source).properties["id"],
                target=target,
                target_id=get_aifNode_by_title(target).properties["id"],
                title=source+" "+schema+" "+target,
                timestamp=timestamp(),
                date=date()
                )
        authorship = Relationship(user, "PUBLISHED", schemaNode)
        graph.create(authorship)
        return schemaNode.properties["id"]

    def add_I_Node(self, title):
        user = self.find()
        iNode = Node(
            "INode",
            id=str(uuid.uuid4()),
            title=title,
            timestamp=timestamp(),
            date=date()
        )
        rel = Relationship(user, "PUBLISHED", iNode)
        graph.create(rel)

    #Tags Stuff
        #tags = [x.strip() for x in tags.lower().split(',')]
        #for t in set(tags):
            #tag = graph.merge_one("Tag", "name", t)
            #rel = Relationship(tag, "TAGGED", post)
            #graph.create(rel)

    def vote_on_aifnode(self, aifNode_id, event_name, vote_type):
        user = self.find()
        aifNode = get_aifNode(aifNode_id)
        cypher_string_find_event = \
            "MATCH (:User {username:'" + user.properties[ "username"] + "'})-[r]->(n:ENode {name:'" + event_name + "'})\
            RETURN count(n) "
        cypher_string_find_vote = \
            "MATCH (vote) WHERE \
            (:User {username:'" + user.properties[ "username"] + "'})-[:VOTED]->(vote:VNode)\
            AND (vote)-[:APPLIES_TO]->(:ENode {name:'" + event_name + "'})\
            AND (vote)-[:APPLIES_TO]->({id:'" + aifNode_id + "'})\
            RETURN vote"
        # check if user observes this event, and that it exists, otherwise, create it.
        vote = graph.evaluate(cypher_string_find_vote)
        if vote is not None:
            vote["name"] = vote_type
            graph.push(vote)
        else:
            if not graph.run(cypher_string_find_event).evaluate():
                event = create_new_event(user, event_name)
            else:
                event = graph.find_one("ENode", "name", event_name)
            create_new_vote(user, vote_type, event, aifNode)

    def get_recent_posts(self):
        query = """
        MATCH (user:User)-[:PUBLISHED]->(aifnode)
        WHERE user.username = {username}
        RETURN aifnode
        ORDER BY aifnode.timestamp DESC LIMIT 500
        """

        return graph.run(query, username=self.username)

    def get_similar_users(self):
        # Find three users who are most similar to the logged-in user
        # based on tags they've both blogged about.
        query = """
        MATCH (you:User)-[:PUBLISHED]->(:INode)<-[:TAGGED]-(tag:Tag),
              (they:User)-[:PUBLISHED]->(:INode)<-[:TAGGED]-(tag)
        WHERE you.username = {username} AND you <> they
        WITH they, COLLECT(DISTINCT tag.name) AS tags, COUNT(DISTINCT tag) AS len
        ORDER BY len DESC LIMIT 3
        RETURN they.username AS similar_user, tags
        """

        return graph.run(query, username=self.username)

    def get_commonality_of_user(self, other):
        # Find how many of the logged-in user's posts the other user
        # has liked and which tags they've both blogged about.
        query = """
        MATCH (they:User {username: {they} })
        MATCH (you:User {username: {you} })
        OPTIONAL MATCH (they)-[:LIKED]->(post:INode)<-[:PUBLISHED]-(you)
        OPTIONAL MATCH (they)-[:PUBLISHED]->(:INode)<-[:TAGGED]-(tag:Tag),
                       (you)-[:PUBLISHED]->(:INode)<-[:TAGGED]-(tag)
        RETURN COUNT(DISTINCT post) AS likes, COLLECT(DISTINCT tag.name) AS tags
        """

        return graph.run(query, they=other.username, you=self.username)[0]

    def register_validation(flash_func, user_name, password):
        if len(user_name) < 1:
            flash_func('Your username must be at least one character.')
            return False
        elif len(password) < 5:
            flash_func('Your password must be at least 5 characters.')
            return False
        elif not User(user_name).register(password):
            flash_func('A user with that username already exists.')
            return False
        else:
            return True
